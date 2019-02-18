lambda:
	chalice --project-dir $(shell pwd)/quickdraw-lambdas deploy --no-autogen-policy

.PHONY: static
static:
	aws s3 sync --delete static/ s3://quickdraw.ixora.io/
	aws configure set preview.cloudfront true
	aws cloudfront create-invalidation --distribution-id E3K20RY7J6A9FO --paths '/*'

all: lambda static
