VERSION 0.8

FROM alpine:3.21

update-all:
    BUILD --pass-args +update-lunar-references
    BUILD --pass-args +update-uipanel-references

update-lunar-references:
    COPY github.com/earthly/lunar-lib:main+ai-context/ai-context references
    SAVE ARTIFACT references AS LOCAL skills/lunar-policy/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-collector/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-sql/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-cataloger/references
    SAVE ARTIFACT references AS LOCAL skills/lunar-config/references

# lunar-uipanel keeps hand-written examples next to its references, so the
# generated paths are saved one by one rather than replacing the directory.
update-uipanel-references:
    RUN apk add --no-cache curl
    COPY github.com/earthly/lunar-lib:main+ai-context/ai-context/component-json component-json
    # The docs site answers a moved page with HTTP 200 and a "Page Not Found"
    # body, so the fetch is checked on content, not on exit status.
    RUN --no-cache curl -fsSL https://docs-lunar.earthly.dev/configuration/lunar-config/uipanels.md -o uipanels.md \
        && grep -Eq '^\| ID +\| Where it appears +\| Parameters +\|' uipanels.md
    SAVE ARTIFACT uipanels.md AS LOCAL skills/lunar-uipanel/references/uipanels.md
    SAVE ARTIFACT component-json AS LOCAL skills/lunar-uipanel/references/component-json

skills:
    COPY --dir \
        skills/earthfile \
        skills/lunar-cataloger \
        skills/lunar-collector \
        skills/lunar-config \
        skills/lunar-policy \
        skills/lunar-sql \
        skills/lunar-uipanel \
        ./skills/
    SAVE ARTIFACT skills/earthfile
    SAVE ARTIFACT skills/lunar-cataloger
    SAVE ARTIFACT skills/lunar-collector
    SAVE ARTIFACT skills/lunar-config
    SAVE ARTIFACT skills/lunar-policy
    SAVE ARTIFACT skills/lunar-sql
    SAVE ARTIFACT skills/lunar-uipanel

install-skills:
    LOCALLY
    ARG CODEX_HOME=$HOME/.codex
    RUN mkdir -p $CODEX_HOME/skills
    RUN rm -rf $CODEX_HOME/skills/earthfile $CODEX_HOME/skills/lunar-cataloger $CODEX_HOME/skills/lunar-collector $CODEX_HOME/skills/lunar-config $CODEX_HOME/skills/lunar-policy $CODEX_HOME/skills/lunar-sql $CODEX_HOME/skills/lunar-uipanel
    COPY +skills/earthfile $CODEX_HOME/skills/earthfile
    COPY +skills/lunar-cataloger $CODEX_HOME/skills/lunar-cataloger
    COPY +skills/lunar-collector $CODEX_HOME/skills/lunar-collector
    COPY +skills/lunar-config $CODEX_HOME/skills/lunar-config
    COPY +skills/lunar-policy $CODEX_HOME/skills/lunar-policy
    COPY +skills/lunar-sql $CODEX_HOME/skills/lunar-sql
    COPY +skills/lunar-uipanel $CODEX_HOME/skills/lunar-uipanel
