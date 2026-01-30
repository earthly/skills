VERSION 0.8

FROM alpine:3.21

update-all:
    BUILD --pass-args +update-lunar-docs
    BUILD --pass-args +update-lunar-references

update-lunar-docs:
    COPY github.com/earthly/lunar:main+docs/docs docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-policy/docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-collector/docs
    SAVE ARTIFACT docs AS LOCAL skills/lunar-sql/docs

update-lunar-references:
    COPY github.com/earthly/lunar-lib:main+ai-context/ai-context references
    SAVE ARTIFACT references AS LOCAL skills/lunar-policy/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-collector/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-sql/references

skills:
    COPY --dir \
        skills/earthfile \
        skills/lunar-collector \
        skills/lunar-policy \
        skills/lunar-sql \
        ./skills/
    SAVE ARTIFACT skills/earthfile
    SAVE ARTIFACT skills/lunar-collector
    SAVE ARTIFACT skills/lunar-policy
    SAVE ARTIFACT skills/lunar-sql

install-skills:
    LOCALLY
    ARG CODEX_HOME=$HOME/.codex
    RUN mkdir -p $CODEX_HOME/skills
    RUN mkdir -p skills-install
    COPY +skills/* ./tmp-skills-install/
    RUN cp -r tmp-skills-install/* $CODEX_HOME/skills/
    RUN rm -rf tmp-skills-install
