# Designer Bootstrap

This one-time bootstrap collects brand assets and design context before design work starts. If this crew is being enabled through Main Agent and has no direct work channel yet, Main Agent may ask these questions on behalf of this crew and write the answers into the crew workspace.

## Step 1: Brand Assets

Collect:

- **Brand name**: company/brand name
- **Brand colors**: primary, secondary, accent, surface, text colors (hex or named)
- **Logo**: location or URL of logo files (if available)
- **Typography**: preferred font families (if any), or note "no preference"
- **Existing brand guidelines**: any existing style guide, brand book, or design documentation location

If the user has no established brand assets, note this — the Designer will help establish them during the first品牌视觉体系构建 task.

## Step 2: Design Preferences

Ask:

- **Default style direction**: any preferred visual style (e.g., minimal, editorial, neo-brutalism, glassmorphism, dark luxury)
- **Common output formats**: what the user typically needs (landing pages, app UI, brand systems, social media assets)
- **Dark mode**: is dark mode needed for deliverables?
- **Approval workflow**: who reviews and approves designs? How many revision rounds are typical?

## Step 3: Environment Verification

On first startup, check and report:

1. `SILICONFLOW_API_KEY` is set → enables `siliconflow-img-gen` for AI image generation
2. `PEXELS_API_KEY` is set → enables `pexels-footage` for stock images
3. `PIXABAY_API_KEY` is set → enables `pixabay-footage` for stock images

At least one image source should be available. If none are configured, report clearly.

## Completion

After bootstrap is complete:

1. Update `MEMORY.md` with brand assets, design preferences, and available image sources.
2. Update `USER.md` with approval workflow if specified.
3. Delete `BOOTSTRAP.md` from the runtime workspace.
4. Suggest the next step, such as starting a brand visual system build or the first design task.
