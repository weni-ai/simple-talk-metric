# lambda-test

This repository manage **AWS lambda** functions code, allowing developers to focus on writing the code.

New image new versions is automatically released whenever a tag is created in the format `X.Y.Z-staging` or `X.Y.Z`.

When a tag following this format is generated, the github actions builds a new image, push to **AWS ECR** and updates the lambda repository to use this image version(if that the version is greater than the current version).

After creating the tags, remember to check the plan and then apply the [changes in this repository](https://github.com/weni-ai/infra-weni-lambda).

[modeline]: # ( vim: set fenc=utf-8 spell spl=en: )
