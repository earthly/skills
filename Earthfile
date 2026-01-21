VERSION 0.8

FROM alpine:3.21

update-all:
    BUILD --pass-args +update-lunar-docs
    BUILD --pass-args +update-lunar-references

update-lunar-docs:
    COPY github.com/earthly/lunar:main+docs/docs docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-policy/docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-collector/docs

update-lunar-references:
    COPY github.com/earthly/lunar-lib:main+ai-context/ai-context references
    SAVE ARTIFACT references AS LOCAL skills/lunar-policy/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-collector/references

install-skills:
    LOCALLY
    ARG CODEX_HOME=$HOME/.codex
    RUN rm -rf $CODEX_HOME/skills/earthfile $CODEX_HOME/skills/lunar-collector $CODEX_HOME/skills/lunar-policy
    RUN cp -r skills/earthfile $CODEX_HOME/skills/earthfile
    RUN cp -r skills/lunar-collector $CODEX_HOME/skills/lunar-collector
    RUN cp -r skills/lunar-policy $CODEX_HOME/skills/lunar-policy
