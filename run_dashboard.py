import argparse
from update_hugging_face_history import *
from update_github_history import *


def main():
    parser = argparse.ArgumentParser(description="Fetch and generate open source community metrics.")
    parser.add_argument('--star', action='store_true', help='Generate GitHub star records.')
    parser.add_argument('--issue', action='store_true', help='Generate GitHub issue records.')
    parser.add_argument('--model_card', action='store_true', help='Generate Hugging Face relevant model cards records')
    parser.add_argument('--all', action='store_true', help='Generate all records: GitHub Star, GitHub Issue, Hugging Face Model Cards.')
    parser.add_argument('--deploy', action='store_true', help='TODO')

    args = parser.parse_args()

    if not any([args.star, args.issue, args.model_card]):
        print("No specific function requested, running all functions.")
        update_github_star()
        update_issue_history()
        update_hugging_face_model_card_history()
        return

    if args.all:
        update_github_star()
        update_issue_history()
        update_hugging_face_model_card_history()
        return

    if args.star:
        update_github_star()

    if args.issue:
        update_issue_history()

    if args.model_card:
        update_hugging_face_model_card_history()


if __name__ == "__main__":
    main()