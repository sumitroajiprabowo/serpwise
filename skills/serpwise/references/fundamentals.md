# SEO fundamentals (Google SEO Starter Guide + Creating helpful content)

Source: developers.google.com/search/docs/fundamentals/* (SEO Starter Guide, How Search works, Creating helpful content, Using generative AI content, Do you need an SEO?) and /essentials

## Contents
1. How Search works & timelines
2. Help Google find content
3. Site organization
4. Helpful, people-first content
5. Links
6. Appearance basics (titles, snippets, images, video)
7. Promotion
8. Myths (don't focus on these)
9. Hiring an SEO and checking third-party advice

## 1. How Search works & timelines
- Three stages, and not every page gets through each one:
  - **Crawling**: Googlebot finds URLs through links, known pages and sitemaps, then fetches and renders them with a recent Chrome.
  - **Indexing**: Google reads the text, `<title>`, alt text, images and video, groups duplicates and picks one canonical, and records signals such as language, country and usability.
  - **Serving**: for each query it picks the most relevant, highest-quality results, using hundreds of factors including location, language and device.
- Google discovers pages with automated crawlers, mostly by following links from pages it already knows. Most sites need no submission.
- Google never takes payment to crawl more often or rank higher, and ads don't affect organic ranking. Appearing in results is free.
- **Search Essentials** has three parts:
  - **Technical requirements**, the minimum for a page to be eligible: Googlebot isn't blocked (robots.txt, login), the page returns HTTP 200, and it has indexable content in a supported file type that doesn't break spam policies.
  - **Spam policies** (spam-policies.md).
  - **Key best practices**: helpful people-first content; the words people search for placed in prominent spots (title, main heading, alt text, link text); crawlable links; telling people about the site; following image, video, structured data and JavaScript guidance; enabling search features that fit the site.
- Meeting all of this makes a page eligible. It does not guarantee crawling, indexing or ranking.
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
- Reduce duplicate content: one URL per piece of content. Redirect non-preferred URLs, or use `rel=canonical`. It is not a spam violation, but it wastes crawl and confuses users. Don't over-worry: Google usually sorts out duplicates on its own.
- Don't reorganize a site right away for SEO. Google understands pages as they are now, and moving URLs has its own cost (crawling-indexing.md §16).

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
- Changing dates or making trivial edits to look fresh. Adding or removing lots of content to look fresh doesn't help either.
- Content that looks mass-produced or outsourced across many creators or sites, sloppy, or hastily made.

Main content quality (what Google's quality raters judge, and what its systems aim to reward):
- **Effort**: real human work. Pages auto-built from feeds, or large volumes of unreviewed AI text, show little to none.
- **Originality**: information or perspective that isn't available elsewhere.
- **Talent or skill**: clear writing, well-made video, tools that work. Not every topic needs a credentialed expert.
- **Accuracy**: factually correct. YMYL content must match expert consensus.

Who / How / Why:
- **Who**: make authorship clear (bylines linking to author pages). No fabricated authors, AI headshots, or fake credentials.
- **How**: disclose automation or AI use where readers would reasonably expect it. Show how products were tested.
- **Why**: the primary purpose must be helping people. Using AI to generate many pages primarily for ranking is scaled content abuse.

Generative AI content (Google's guidance on using it on a site):
- AI is fine for research and for structuring original work. Many pages generated without added value are scaled content abuse.
- Models predict likely text and can hallucinate. Fact-check everything before publishing, including the `<title>`, meta description, structured data and alt text, since those show in results.
- Tell readers how content was made where they would wonder, and add image metadata where relevant.
- Merchant Center (Shopping, not organic Search): AI-generated images need IPTC `DigitalSourceType` = `TrainedAlgorithmicMedia`, and AI-generated product titles or descriptions must be labelled as such.

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

## 9. Hiring an SEO and checking third-party advice
- A small local business can do most of the work itself, starting from the SEO Starter Guide. Learning the basics also helps you spot bad advice.
- The best time to bring one in is before a redesign or a new site, not after launch.
- Questions to ask: examples of past work; do they follow Search Essentials; what results, in what time, measured how; experience in your industry, country and with international sites; how they communicate and whether they explain every change. A good one asks what makes your business unique and how your customers find you.
- For an audit, give read-only Search Console access, not write access.
- Red flags:
  - unsolicited emails offering SEO;
  - a guaranteed #1 ranking;
  - a "special relationship" with Google or "priority submit";
  - secrecy or vague plans; you are responsible for what they do on your site;
  - requiring a link to them, link schemes, or submitting to "thousands of search engines".
- Third-party SEO tools have no access to Google's internal ranking data, and none is "approved" by Google. Before acting on a third-party audit, check that it cites Google documentation.
- "AEO" and "GEO" advice for AI search should be checked against Google's own guide for generative AI features (appearance.md §13). To Google, that work is still SEO.
- Deceptive SEO firms can be reported to the FTC in the US, or through econsumer.gov elsewhere.
