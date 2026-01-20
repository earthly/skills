VERSION 0.8

FROM alpine:3.21

update-all:
    BUILD --pass-args +update-lunar-docs
    BUILD --pass-args +update-lunar-references

update-lunar-docs:
    COPY github.com/earthly/lunar:vlad/docs-export+docs/docs docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-policy/docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-collector/docs

update-lunar-references:
    COPY github.com/earthly/lunar-lib:main+ai-context/ai-context references
    SAVE ARTIFACT references AS LOCAL skills/lunar-policy/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-collector/references
