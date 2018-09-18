lambda:
	chalice --project-dir $(shell pwd)/quickdraw-lambdas deploy --no-autogen-policy

.PHONY: static
static:
	aws s3 sync --delete static/ s3://quickdraw.ixora.io/
	aws configure set preview.cloudfront true
	aws cloudfront create-invalidation --distribution-id E1RBOK9SPC7E2K --paths '/*'

all: lambda static
