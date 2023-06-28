#!/usr/bin/env python3
"""
Run gitlab-ci.yml linting on multiple gitlab repositories in a row.
"""

# import our used python libraries
import logging
from argparse import ArgumentParser
from gitlab import Gitlab, GitlabListError, GitlabAuthenticationError
from git import Repo, GitCommandError
from jinja2 import Environment, FileSystemLoader


def get_projects():
    """Get a list of all projects."""
    try:

        if args.scan_repo:
            logging.info("fetch %s from %s", args.scan_repo, gitlab_url)
            projects = gl.projects.list(
                search=args.scan_repo, order_by="id", min_access_level=20, archived=False, with_issues_enabled=True
            )
        else:
            logging.info("fetch list of all projects from %s", gitlab_url)
            projects = gl.projects.list(
                get_all=True, order_by="id", min_access_level=20, archived=False, with_issues_enabled=True
            )
        logging.debug(projects)
        return projects
    except GitlabListError:
        logging.error("can't fetch list from %s", gitlab_url)
    except GitlabAuthenticationError:
        logging.error("cannot authenticate against %s", gitlab_url)


def create_description(scanner_output):
    """Create the description for the issue."""
    env = Environment(loader=FileSystemLoader("./templates/"))

    template = env.get_template(f"{args.template_name}")
    description = template.render(scanner_output=scanner_output.errors)

    return description


def close_issue(project):
    """Close the issue if linting is successful."""
    issue_list = project.issues.list(labels=["automated-linting-scan"])
    issues_fixed = 0

    if len(issue_list) > 0:
        issue = issue_list[0]
        if issue.state == "opened":
            issues_fixed = 1
            issue.state_event = "close"
            comment_text = (
                "Closed by the linting scanner because linting is fine."
            )
            issue.notes.create({"body": comment_text})
            issue.save()

    return issues_fixed


def create_issue(project, scanner_output):
    """Create an issue if we found something with our scan."""
    issue_list = project.issues.list(labels=["automated-linting-scan"])

    if len(issue_list) > 0:
        logging.debug("there is already an issue")
        issue = issue_list[0]
        if issue.state == "closed":
            issue.state_event = "reopen"
            comment_text = (
                "Reopened by the linting scanner because linting found an error."
            )
            issue.notes.create({"body": comment_text})
        issue.description = create_description(scanner_output=scanner_output)
        issue.save()
    else:
        project.issues.create(
            {
                "title": "Automated linting scan",
                "description": create_description(scanner_output=scanner_output),
                "labels": ["automated-linting-scan"],
            }
        )

    issues_found = 1
    return issues_found


def run_scan(
    project, project_path, projects_with_issues_found, projects_with_issues_fixed
):
    """Scan a project."""

    logging.info("%s: starting linting scan", project_path)
    lint_result = project.ci_lint.get()
    logging.debug(lint_result)
    if "Please provide content of .gitlab-ci.yml" not in lint_result.errors and not lint_result.valid:
        logging.info(
            "%s: linting is broken - create a ticket", project_path
        )
        projects_with_issues_found += create_issue(
            project=project, scanner_output=lint_result
        )
    elif lint_result.valid:
        projects_with_issues_fixed += close_issue(project=project)
        logging.info("%s: linting okay.", project_path)
    else:
        logging.info("%s: linting failed - skip issue creation", project_path)

    return projects_with_issues_fixed, projects_with_issues_found

if __name__ == "__main__":
    # initialize logging and set it to INFO
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%d/%m/%y %H:%M:%S",
    )

    parser = ArgumentParser()
    parser.add_argument(
        "--scan-repo",
        help="scan explicit repo with this name",
        required=False,
        default=False,
        dest="scan_repo",
    )
    parser.add_argument(
        "--gitlab-hostname",
        help="hostname of gitlab (e.g. git.example.com)",
        required=True,
        dest="gitlab_hostname",
    )
    parser.add_argument(
        "--gitlab-access-token",
        help="access token for project or projects",
        required=True,
        dest="gitlab_access_token",
    )
    parser.add_argument(
        "--template-name",
        help="name of the template file used for the ticket description",
        required=False,
        default="default_issue_description.j2",
        dest="template_name",
    )
    args = parser.parse_args()

    gitlab_url = f"https://{args.gitlab_hostname}"
    gitlab_url_with_login = (
        f"https://scanner:{args.gitlab_access_token}@{args.gitlab_hostname}"
    )

    # login to gitlab with private token
    gl = Gitlab(gitlab_url, private_token=args.gitlab_access_token)
    P_WITH_ISSUES_FIXED = 0
    P_WITH_ISSUES_FOUND = 0
    for p in get_projects():
        p_id = getattr(p, "id")
        p_path = getattr(p, "path_with_namespace")
        p_url = f"{gitlab_url_with_login}/{p_path}.git"

        # skip project if there is an issue to disable scanning
        if len(p.issues.list(labels=["automated-linting-scan-disabled"])) > 0:
            logging.info(
                '%s has label "automated-linting-scan-disabled" - skipping', p_path
            )
            continue

        run_scan(
            project=p,
            project_path=p_path,
            projects_with_issues_fixed=P_WITH_ISSUES_FIXED,
            projects_with_issues_found=P_WITH_ISSUES_FOUND,
        )

    logging.info("issues found: %s", P_WITH_ISSUES_FOUND)
    logging.info("issues fixed: %s", P_WITH_ISSUES_FIXED)
