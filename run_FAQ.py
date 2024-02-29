import argparse
from generate_FAQ import *

def call_wechat_FAQ(args):
    filename, chunk, overlap = args.filename, args.chunk, args.overlap
    print(f'Generating FAQ from WeChat messages in {filename} with chunk_size of {chunk} and overlap of {overlap}')
    wechat_to_faq(filename, chunk, overlap)


def call_github_FAQ(args):
    owner, repo = args.owner, args.repo
    print(f'Generating FAQ from GitHub issues from {owner}:{repo}')
    github_to_faq(owner, repo)


def main():
    parser = argparse.ArgumentParser(description="Generate FAQ from WeChat messages or GitHub issues.")
    parser.add_argument('--wechat', action='store_true', help='Generate FAQ based on WeChat messages')
    # TODO: Due to 200k request limit
    parser.add_argument('--github', action='store_true', help='Generate GitHub issue records.')
    parser.add_argument('--filename', default='./wechat/message.csv', help='Path to generated WeChat message file. '
                                                                           'Default: ./wechat/message.csv')
    parser.add_argument('--chunk', default=100, help='The size of each message chunk. Default: 100 messages per '
                                                     'request.')
    parser.add_argument('--overlap', default=20, help='The number of messages that overlaps with previous message '
                                                      'chunk. Default: 20 message per chunk')
    parser.add_argument('--owner', default='01-ai', help='The owner of GitHub repo')
    parser.add_argument('--repo', default='Yi', help='The name of GitHub repo')

    args = parser.parse_args()

    if not any([args.wechat, args.github]):
        call_wechat_FAQ(args)
        call_github_FAQ(args)
        return

    if args.wechat:
        call_wechat_FAQ(args)
        return

    if args.github:
        call_github_FAQ(args)

if __name__ == "__main__":
    main()