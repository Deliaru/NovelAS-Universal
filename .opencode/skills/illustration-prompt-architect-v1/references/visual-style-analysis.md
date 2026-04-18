# Visual Style Analysis Framework

## Purpose

This framework helps you analyze reference images and extract **transferable visual patterns** without attributing them to specific artists. The goal is to describe the visual system in a way that can be replicated across different subjects and scenes.

## Why Not Name Artists?

1. **Legal/ethical concerns**: Artist attribution in prompts raises copyright questions
2. **Technical unreliability**: Models may not know the artist or may associate wrong patterns
3. **Transferability**: Describing the visual system is more flexible than invoking a name
4. **Specificity**: "Clean cel-shading with rim lighting" is clearer than "Artist X style"

## Analysis Dimensions

### 1. Line Treatment (线条处理)

**What to observe:**
- Line weight variation (uniform vs varied)
- Edge treatment (sharp vs soft, where each is used)
- Line color (black, colored, or absent)
- Completeness (fully outlined vs suggested edges)

**Extraction pattern:**

Observe multiple images and identify:
- Which elements get crisp lines (usually: character face, hands, key objects)
- Which elements get soft edges (usually: background, atmospheric effects, distant elements)
- Whether lines are uniform weight or vary by importance
- Whether outlines are black, colored to match fill, or absent

**Example output:**
"Line treatment uses clear hierarchy: character facial features, hands, and clothing edges have confident, medium-weight black outlines. Background elements have softer, thinner lines or suggested edges. No uniform line weight - important elements are emphasized through line clarity rather than thickness."

**Common patterns:**

- **Cel-shading style (赛璐璐风格)**: Clean, uniform black outlines, sharp edges throughout
- **Soft illustration (柔和插画)**: Minimal or no outlines, edges defined by color/value changes
- **Selective outlining (选择性描边)**: Outlines only on key elements, background has soft edges
- **Colored lines (彩色线稿)**: Outlines match or complement fill colors rather than being black

### 2. Color Organization (色彩组织)

**What to observe:**
- Palette size (limited vs extensive)
- Saturation levels (vibrant vs muted)
- Color relationships (complementary, analogous, monochromatic)
- How colors are distributed (dominant + accent pattern)

**Extraction pattern:**

Identify:
- Dominant color family (占60-70%的主色调)
- Accent colors (强调色, 10-20%)
- How saturation varies by depth (foreground vs background)
- Whether colors are pure or grayed/muted
- Color temperature bias (warm vs cool)

**Example output:**
"Color organization uses limited palette: cool blue-gray dominates 70% of the image (sky, shadows, background). Warm accent colors (amber, soft orange) appear in 20% (character's eyes, key light sources). Remaining 10% is neutral whites and grays. Saturation decreases with distance - foreground has full saturation, background is desaturated by 40%."

**Common patterns:**

- **Dominant + accent (主色+强调色)**: One color family dominates, small amounts of complementary color for focus
- **Analogous harmony (类似色和谐)**: Colors next to each other on color wheel (blue-green-cyan)
- **Monochromatic + pop (单色+跳色)**: Mostly one color with different values, one contrasting accent
- **Desaturated + pure (低饱和+纯色)**: Muted overall palette with small areas of pure, saturated color

### 3. Rendering Method (渲染方式)

**What to observe:**
- Shading style (cel-shaded, soft gradient, painterly)
- Texture presence (smooth vs textured)
- Detail density (clean vs complex)
- Finish quality (flat, glossy, matte)

**Extraction pattern:**

Determine:
- How shadows are rendered (hard edge, soft gradient, or absent)
- Whether surfaces are smooth or textured
- How much detail is present in different areas
- Whether there's a "painted" quality or "digital clean" quality

**Example output:**
"Rendering uses soft gradient shading rather than hard cel-shading. Shadows transition smoothly from light to dark with subtle color shifts (warm to cool). Surfaces are smooth with minimal texture. Detail is concentrated on character, background is simplified with broad color areas. Overall finish is clean and polished, not painterly or textured."

**Common patterns:**

- **Cel-shading (赛璐璐上色)**: Flat color fills with hard-edged shadows, 2-3 value levels
- **Soft shading (柔和渐变)**: Smooth gradients, many value levels, no hard edges
- **Painterly (绘画感)**: Visible brushstrokes, texture, color mixing
- **Flat graphic (平面图形)**: Minimal shading, mostly flat colors, shape-based design

### 4. Spatial Depth System (空间深度系统)

**What to observe:**
- How foreground/midground/background are separated
- Use of atmospheric perspective
- Overlap and occlusion patterns
- Detail hierarchy by depth

**Extraction pattern:**

Identify:
- How many distinct depth planes are present
- What techniques separate them (atmospheric haze, detail reduction, color shift)
- Whether depth is emphasized or minimized
- How character integrates with environment

**Example output:**
"Spatial depth uses three clear planes: soft-focus foreground elements (flowers, particles) frame the composition, sharp-focus midground contains the character with full detail, simplified background fades into atmospheric haze with 50% detail reduction and cooler color temperature. Depth is emphasized through this clear separation rather than complex perspective."

**Common patterns:**

- **Three-plane separation (三层分离)**: Distinct foreground/midground/background with different treatment
- **Flat decorative (平面装饰)**: Minimal depth, pattern-like background, character as focal plane
- **Atmospheric depth (大气纵深)**: Gradual fading and color shift with distance
- **Integrated space (整合空间)**: Character and environment rendered with equal detail, unified space

### 5. Composition Patterns (构图模式)

**What to observe:**
- Subject placement (centered, rule of thirds, dynamic)
- Framing devices (foreground elements, vignetting)
- Negative space usage
- Visual flow and eye guidance

**Extraction pattern:**

Identify:
- Where subjects are typically placed
- How negative space is used
- Whether compositions are symmetrical or asymmetric
- How viewer's eye is guided through the image

**Example output:**
"Composition typically places character in right third of frame, with left third devoted to environmental context or negative space. Foreground elements (branches, architectural details) frame the character without obscuring them. Diagonal lines guide eye from upper left to lower right. Asymmetric balance with character as visual weight anchor."

**Common patterns:**

- **Center-weighted (中心构图)**: Subject centered, often symmetrical
- **Rule of thirds (三分法)**: Subject at intersection points, balanced with environment
- **Dynamic diagonal (动态对角)**: Elements arranged along diagonal lines, creates movement
- **Environmental frame (环境框架)**: Character framed by foreground/background elements

### 6. Lighting Approach (光影方法)

**What to observe:**
- Light source clarity (single clear source vs ambient)
- Shadow behavior (hard, soft, colored, absent)
- Highlight treatment (sharp, soft, colored)
- Overall value range (high contrast vs low contrast)

**Extraction pattern:**

Determine:
- Whether lighting is naturalistic or stylized
- How shadows are colored and shaped
- Where highlights appear and how they're rendered
- Overall contrast level

**Example output:**
"Lighting uses single clear directional source (usually from upper side) creating soft-edged shadows. Shadows are colored (cool blue-gray in outdoor scenes, warm brown in indoor) rather than black. Highlights are subtle and selective - concentrated on hair, eyes, and key reflective surfaces. Overall contrast is moderate (40-50% shadow density), maintaining readability throughout."

**Common patterns:**

- **Dramatic single source (戏剧性单光源)**: Strong directional light, high contrast, clear shadows
- **Soft ambient (柔和环境光)**: Diffuse lighting, minimal shadows, low contrast
- **Rim-lit (轮廓光)**: Backlight emphasis, creates glowing edges
- **Flat graphic (平面图形光)**: Minimal lighting variation, shape-based rather than light-based

### 7. Material Rendering (材质表现)

**What to observe:**
- How different materials are distinguished (fabric, metal, glass, skin)
- Reflectivity levels
- Transparency treatment
- Surface texture indication

**Extraction pattern:**

Identify:
- How many material types are clearly differentiated
- What visual cues distinguish them (highlights, texture, transparency)
- Whether materials are realistic or stylized
- How much detail is given to material properties

**Example output:**
"Material rendering clearly differentiates 3-4 material types: fabric has soft shading with subtle folds, no strong highlights; skin has smooth gradients with slight subsurface warmth; metal has sharp specular highlights on edges; glass has minimal refraction, mostly indicated by edge highlights. Materials are stylized rather than photorealistic - simplified to essential visual cues."

**Common patterns:**

- **Simplified material (简化材质)**: Minimal differentiation, mostly indicated by color
- **Selective realism (选择性写实)**: Key materials (skin, hair) detailed, others simplified
- **Uniform stylization (统一风格化)**: All materials rendered with same level of abstraction
- **Material showcase (材质展示)**: Strong differentiation, materials are visual focus

### 8. Detail Distribution (细节分布)

**What to observe:**
- Where detail is concentrated
- How detail density changes across the image
- What gets simplified or omitted
- Balance between detailed and rest areas

**Extraction pattern:**

Map:
- High detail zones (usually character face, hands, key objects)
- Medium detail zones (usually character clothing, immediate environment)
- Low detail zones (usually background, atmospheric elements)
- How transitions between zones are handled

**Example output:**
"Detail distribution follows clear hierarchy: character face and hands receive highest detail (individual eyelashes, finger definition, fabric texture). Character clothing and hair have medium detail (major folds and strands, simplified texture). Background has minimal detail (broad color areas, suggested forms, no fine texture). Transitions are smooth - no jarring jumps in detail level."

**Common patterns:**

- **Character-focused (角色集中)**: All detail on character, background minimal
- **Balanced (平衡分布)**: Character and environment receive similar detail levels
- **Selective focus (选择性聚焦)**: Detail concentrated on narrative focal point, rest simplified
- **Overall high detail (整体高细节)**: Consistent detail throughout, no major simplification

## Analysis Workflow

### Step 1: Initial Observation

Look at 3-5 reference images (if available) and note:
- First impression (clean, painterly, graphic, atmospheric, etc.)
- Most distinctive visual characteristic
- What makes these images feel cohesive

### Step 2: Systematic Analysis

Go through each dimension above and extract patterns:
- What's consistent across multiple images?
- What varies (and is therefore not part of the core style)?
- What's the most important characteristic to preserve?

### Step 3: Synthesis

Combine observations into a coherent style description:
- Lead with the most distinctive characteristics
- Organize from macro (composition, color) to micro (line, detail)
- Use concrete visual terms, not abstract aesthetic judgments

### Step 4: Transferability Test

Ask: "If I describe this to someone who hasn't seen the references, can they visualize it?"
- ✗ Bad: "Beautiful, atmospheric, high quality"
- ✓ Good: "Soft gradient shading, cool blue-gray dominant palette with warm accents, three-plane depth separation"

## Example: Complete Style Analysis

**Reference context:** User provides 3 images of indoor character scenes with consistent visual approach.

**Analysis output:**

"Visual style analysis:

**Composition**: Characters positioned in right or left third of frame, with significant negative space devoted to environmental context. Foreground elements (window frames, furniture edges) create natural framing without obscuring the subject. Asymmetric balance with character as visual anchor.

**Line treatment**: Selective outlining - character facial features, hands, and key clothing edges have medium-weight, confident lines. Background architecture and distant elements have softer, suggested edges or no outlines. Line weight varies by importance rather than being uniform.

**Color organization**: Limited palette with cool-warm contrast. Dominant cool tones (blue-gray, desaturated cyan) occupy 60-70% of image in backgrounds and shadows. Warm accents (amber, soft orange, peachy skin tones) concentrate on character and key light sources. Saturation decreases with distance - foreground maintains full color, background desaturates by 30-40%.

**Rendering**: Soft gradient shading rather than cel-shading. Shadows transition smoothly with subtle color shifts (warm to cool). Surfaces are smooth with minimal texture. Detail concentrates on character, background simplifies to broad color areas. Clean, polished finish.

**Lighting**: Single clear directional light source (usually window light from side) creates soft-edged shadows. Shadows are colored (cool blue-gray) not black. Highlights are selective - concentrated on hair, eyes, reflective surfaces. Moderate contrast (40-50% shadow density) maintains readability.

**Spatial depth**: Three distinct planes - soft foreground framing, sharp character midground, simplified atmospheric background. Depth emphasized through detail reduction and color temperature shift rather than complex perspective.

**Materials**: Simplified material rendering - fabric has soft shading with subtle folds, skin has smooth gradients, hard surfaces have minimal specular highlights. Materials are stylized to essential visual cues rather than photorealistic.

**Detail distribution**: High detail on character face and hands, medium detail on clothing and hair, low detail on background. Smooth transitions between detail levels, no jarring jumps."

## Common Pitfalls to Avoid

### Pitfall 1: Describing Content Instead of Style

✗ Bad: "Images show girls in school uniforms in classrooms"
✓ Good: "Line treatment uses selective outlining with emphasis on character features"

**Why:** Content is what's depicted, style is how it's depicted. Focus on the "how."

### Pitfall 2: Using Vague Aesthetic Terms

✗ Bad: "Beautiful, atmospheric, high quality, professional"
✓ Good: "Soft gradient shading, cool-dominant palette, three-plane depth separation"

**Why:** Vague terms don't give the model actionable visual instructions.

### Pitfall 3: Over-Specifying Incidental Details

✗ Bad: "Character has blue hair, wears white dress, holds book"
✓ Good: "Character details are rendered with higher line clarity than background elements"

**Why:** Specific content details aren't part of the transferable style system.

### Pitfall 4: Naming Artists or Invoking Existing Styles

✗ Bad: "Like Artist X's style" or "Kyoto Animation style"
✓ Good: "Clean line art with soft gradient shading, selective detail distribution"

**Why:** Legal concerns, technical unreliability, and lack of specificity.

### Pitfall 5: Listing Everything Without Hierarchy

✗ Bad: Equal detail on all 8 dimensions regardless of importance
✓ Good: Lead with 2-3 most distinctive characteristics, briefly note others

**Why:** Not all dimensions are equally important for every style. Prioritize what matters most.

## Integration into Prompts

Once you've analyzed the style, integrate it into the prompt's **style layer**:

```
[Subject, action, camera, environment layers...]

The illustration uses [most distinctive style characteristic]. [Line treatment description]. [Color organization description]. [Rendering method description]. [Lighting approach description]. [Spatial depth description if relevant].
```

**Example integration:**

"The illustration uses soft gradient shading with selective line emphasis. Character facial features, hands, and key clothing edges have confident medium-weight outlines, while background elements have softer suggested edges. Color palette is cool-dominant (blue-gray, desaturated cyan) with warm accents (amber, peachy tones) concentrated on character and light sources. Shading uses smooth gradients rather than hard cel-shading, with colored shadows (cool blue-gray) maintaining readability. Single directional light source from the left creates soft-edged shadows. Spatial depth is established through three planes: soft foreground framing, sharp character midground, simplified atmospheric background."

## Quick Reference: Style Dimensions

| Dimension | Key Question | Output Format |
|-----------|-------------|---------------|
| Line Treatment | Where are lines crisp vs soft? | "Lines are [quality] on [elements], [quality] on [elements]" |
| Color Organization | What's the dominant color system? | "[Color family] dominates [%], [accent colors] at [%]" |
| Rendering Method | How are surfaces and shadows rendered? | "Rendering uses [method] with [characteristics]" |
| Spatial Depth | How is depth created? | "Depth established through [technique]" |
| Composition | Where is subject placed? | "Subject positioned [location], [framing approach]" |
| Lighting | What's the light source setup? | "[Number] light source from [direction], [shadow behavior]" |
| Materials | How are materials differentiated? | "Materials simplified to [approach]" |
| Detail Distribution | Where is detail concentrated? | "Detail hierarchy: [high] on [elements], [low] on [elements]" |

## Final Note

Style analysis is about finding the **transferable visual system** - the rules and patterns that can be applied to new subjects and scenes. Focus on the "how" of visual construction, not the "what" of content. Be specific, concrete, and actionable in your descriptions.
