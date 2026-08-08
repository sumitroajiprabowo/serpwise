# SEO fundamentals (Google SEO Starter Guide + Creating helpful content)

Source: developers.google.com/search/docs/fundamentals/seo-starter-guide, /creating-helpful-content

## Contents
1. How Search works & timelines
2. Help Google find content
3. Site organization
4. Helpful, people-first content
5. Links
6. Appearance basics (titles, snippets, images, video)
7. Promotion
8. Myths (don't focus on these)

## 1. How Search works & timelines
- Google discovers pages with automated crawlers, mostly by following links from pages it already knows. Most sites need no submission.
- Search Essentials define eligibility. Following them does not guarantee indexing.
- Impact of changes appears anywhere from hours to months. Wait a few weeks before judging, and iterate.
- If short on time, hiring an SEO is fine, but vet them (do-i-need-seo page).

## 2. Help Google find content
- Check indexing: `site:example.com` (not exhaustive; the URL Inspection tool is authoritative).
- Not indexed? Check the technical requirements: Googlebot not blocked, page returns 200, indexable content.
- Discovery comes through links (internal and external) and promotion. A sitemap is optional but helpful.
- Google must see the page like a user does: don't block CSS/JS/images needed for rendering. Googlebot crawls mostly from the US, so check geo-varying content.
- Opt-out: noindex, password, or removal (see crawling-indexing.md).

## 3. Site organization
- Use descriptive URLs with words (`/pets/cats.html`, not `/2/6772756D`). URL words can appear as breadcrumbs.
- Group topically similar pages in directories. This helps Google learn per-directory change frequency, which matters at thousands of URLs or more.
- Reduce duplicate content: one URL per piece of content. Redirect non-preferred URLs, or use `rel=canonical`. It is not a spam violation, but it wastes crawl and confuses users.
- Don't restructure an existing site just for SEO unless it's large and messy.

## 4. Helpful, people-first content (the biggest lever)
Google says compelling, useful content likely influences results more than any other factor.

Content should be:
- **Easy to read and well organized**: natural writing, no spelling or grammar errors, paragraphs, headings.
- **Unique**: built on your own knowledge. Don't copy or rehash (scraping is a spam policy).
- **Up to date**: refresh or delete stale content.
- **Helpful, reliable, people-first**: show expertise and experience; cite sources.
- **Anticipating searcher vocabulary**: e.g. "charcuterie" vs "cheese board". There's no need to cover every variant, since Google understands synonyms.
- **Free of distracting ads** that block reading.

Self-assessment questions (Google's list, paraphrased):
- Original information, reporting, research, or analysis?
- Substantial, complete description of the topic? Insight beyond the obvious?
- If drawing on other sources, does it add substantial value rather than just rewriting?
- Does the headline describe the content helpfully, without exaggeration or shock?
- Would you bookmark, share, or recommend it? Would it appear in a print magazine or book?
- Clear sourcing and evidence of expertise? An About page and author info?
- Written by an expert or enthusiast who knows the topic well? Free of easily verified factual errors?
- Good page experience?

People-first signals:
- An existing or intended audience that would find it useful if it came directly to you.
- First-hand experience is shown (used the product, visited the place).
- The site has a primary purpose or focus.
- The reader leaves feeling they learned enough to reach their goal.

Search-engine-first warning signs (avoid):
- Content made mainly to attract search visits, or lots of topics chosen only for traffic.
- Heavy automation across many topics, or mainly summarizing others without adding value.
- Writing about trends just because they trend.
- Readers need to search again for better information.
- Writing to a target word count (Google has no preferred count).
- Entering a niche without real expertise, just for traffic.
- Promising answers that don't exist (e.g. a release date that hasn't been confirmed).
- Changing dates or making trivial edits to look fresh.

Who / How / Why:
- **Who**: make authorship clear (bylines linking to author pages). No fabricated authors, AI headshots, or fake credentials.
- **How**: disclose automation or AI use where readers would reasonably expect it. Show how products were tested.
- **Why**: the primary purpose must be helping people. Using AI to generate many pages primarily for ranking is scaled content abuse.

E-E-A-T:
- Not a ranking factor in itself. Systems use a mix of signals that align with it.
- Trust matters most. YMYL topics (health, finance, safety, civic) get more weight on reliability.
- Quality raters don't directly affect rankings.

## 5. Links
- Links are how Google finds most new pages, and they can corroborate content.
- Use descriptive anchor text: concise, relevant, not "click here", not keyword-stuffed.
- Link to trusted sources when they help. Use `nofollow` only for sources you don't trust.
- UGC (comments, forums): have the CMS add `rel="ugc"` or `nofollow` automatically.

## 6. Appearance basics
- **Title**: unique per page, clear, concise, accurate. May include the brand or location. CMSes usually map the post title to `<title>`.
- **Meta description**: short, unique, summarizing the most relevant points. The snippet is usually taken from page content, so the page text matters.
- **Images**: high quality, near relevant text, descriptive alt text.
- **Video**: a standalone watch page near relevant text, with a descriptive title and description.
- Details are in appearance.md.

## 7. Promotion
- Channels: social media, community engagement, offline and online ads, word of mouth (the most effective and lasting), business cards, posters, and opt-in newsletters.
- Over-promotion fatigues people, and some tactics count as manipulation (spam policies).

## 8. Myths: things Google says not to focus on
| Myth | Google's position |
|---|---|
| Meta keywords | Not used |
| Keyword stuffing | Against spam policies |
| Keywords in domain or URL | Hardly any effect beyond breadcrumbs |
| TLD choice | Only matters for country targeting, and even then low impact. `.com` vs `.guru` makes no difference |
| Content length | No magic minimum or maximum |
| Subdomain vs subdirectory | Choose by business needs |
| PageRank | Just one of many signals |
| Duplicate content "penalty" | No penalty, just inefficient. Copying others is different (scraping) |
| Number or order of headings | Google doesn't need semantic order (good for accessibility though). No ideal count |
| E-E-A-T as a ranking factor | No |
