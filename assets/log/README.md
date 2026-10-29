# Decision and change log

Copy this folder's README.md, build.py and viewer.tpl.html into `<project>/log/`, then create `decisions.md`, `changes.md` and `img/` there.
The log serves two purposes: the user reviews the work later (复盘), and it becomes the case study. The user set these rules on 2026-10-29.

- **Separate entries:**
  - decisions:
    - every board pick;
    - every rejection or reversal;
    - every call Claude makes overnight;
    - every client feedback round;
    - every go-ahead for production.
  - changes:
    - every deploy (draft or production);
    - every site-wide change;
    - every `src` snapshot;
    - every new component or script.
  - Small fixes don't get their own entry. They go into one `daily` change entry per day.
- **Language:** every entry is bilingual (Chinese and English). The viewer switches the whole log between the two, and quotes stay in their original language.
- **Screenshots:** before, after, and the board at the moment of the decision, saved in `img/` as JPGs about 1600px wide.
- **Private material:** partnership terms, pricing, clients' internal details and unsigned testimonials get `private: yes`. Case-study mode hides them.
- **New projects:** backfill from the project's start, using the transcripts (user messages with timestamps), memory, boards, briefs and the client's task tool.
- **Several sessions:** when the work is split across sessions, one logs session writes the entries. The other sessions send it the facts: what, when (UTC), the exact words, deploy IDs, snapshot paths, test counts and screenshot paths.

## Entry format

Each entry is a `###` heading followed by `- key: value` lines. Each value fits on one line. Keys can repeat (for example `quote`).

```
### D-031
- date: 2026-10-29
- time: 17:34
- type: board
- private: no
- title.zh: 首屏改成产品目录
- title.en: Hero becomes a product catalogue
- asked.zh: 客户在 Asana 子任务里要产品像抠图一样单独出现，不要框
- asked.en: The client asked in an Asana subtask for products shown as cut-outs, with no frame
- quote: "<the client's sentence, verbatim>" — <client name>, Asana, 2026-10-29
- decided.zh: 用户，在方案板 Q2
- decided.en: The user, on board Q2
- options: H1 line-up · H2 scatter · H3 hero piece · **H4 catalogue**
- why.zh: 未说明
- why.en: Not stated
- rejected.zh: H1 陈列线（推荐项）
- rejected.en: H1 line-up (the recommended option)
- outcome.zh: 开发会话做了 HeroCatalogue.astro，草稿 <deploy id>
- outcome.en: Built as HeroCatalogue.astro by the development session; draft <deploy id>
- links: options/round-2/board.html · website/src/components/hero/HeroCatalogue.astro
- img: img/D-031-board.jpg · img/D-031-after.jpg
- source: transcript 2026-10-29T17:34; options/round-2/board.html
```

**Decisions (`### D-nnn`)**
- `type` is one of:
  - `board`: a pick on an option board;
  - `reject`: a rejection or reversal;
  - `night`: a call Claude made alone overnight;
  - `client`: a client feedback round and how it was sorted;
  - `prod`: a go-ahead for production;
  - `method`: a change to how the work is done.
- Fields:
  - `title`;
  - `asked` (who raised it, and how);
  - `quote` (verbatim, with who said it, where, and the date);
  - `decided` (who decided, and where);
  - `options` (the picked option in `**bold**`);
  - `why`;
  - `rejected`;
  - `outcome`;
  - `links`, `img` and `source`.

**Changes (`### C-nnn`)**
- `type` is one of: `deploy`, `site`, `snapshot`, `component`, `daily`.
- Fields:
  - `title`;
  - `what` (what changed);
  - `why`;
  - `verify` (how it was checked, with counts);
  - `rollback` (the snapshot, or the deploy to go back to);
  - `links`, `img` and `source`.

**Rules**
- `time` is UTC (`HH:MM`), taken from the session transcript when it's known.
- Quote the user and the client word for word, in their original language.
- `why` only records reasons someone actually gave. If nobody gave one, write `未说明` / `Not stated`. Never make up a reason after the fact.
- When a decision is later reversed, log the reversal as a new entry and note it in the old entry's `outcome`.
- Number entries in date order. When you append, read the last ID first.
- Build the viewer with `python3 log/build.py`. It writes `log/index.html`.
- To add new entries, write them with bare `### D` / `### C` headings in a scratch file and run `python3 log/append.py <file>`. It assigns the next IDs, copies `img.src:` images into `img/`, screenshots `img.url:` pages (needs the `PW` playwright path), and rebuilds the viewer.
