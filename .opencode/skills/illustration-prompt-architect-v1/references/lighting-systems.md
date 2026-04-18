# Lighting Systems for Anime Illustration

## Light Source Types

### Natural Light Sources

**Sunlight (日光)**

*Morning (早晨, 6-9 AM):*
- Color: Warm yellow-orange, soft
- Direction: Low angle, long shadows
- Mood: Fresh, hopeful, gentle
- Implementation: "Soft morning sunlight from the left at 20° angle, casting long gentle shadows. Light has warm peachy-yellow tone."

*Midday (正午, 11 AM-2 PM):*
- Color: Neutral white, high intensity
- Direction: Overhead, short shadows
- Mood: Bright, energetic, harsh
- Implementation: "Strong overhead sunlight creating short, defined shadows directly below objects. Light is neutral white with high contrast."

*Afternoon (下午, 3-5 PM):*
- Color: Warm golden
- Direction: Medium angle, moderate shadows
- Mood: Warm, nostalgic, comfortable
- Implementation: "Golden afternoon sunlight from the right at 45° angle. Warm amber tones with soft, medium-length shadows."

*Sunset/Golden Hour (日落/黄金时段, 5-7 PM):*
- Color: Deep orange, red, purple
- Direction: Low angle, very long shadows
- Mood: Dramatic, romantic, melancholic
- Implementation: "Low-angle sunset light from behind, creating rim lighting on character's silhouette. Deep orange transitioning to purple in shadows."

*Overcast (阴天):*
- Color: Cool neutral, desaturated
- Direction: Diffuse, no clear direction
- Mood: Calm, subdued, introspective
- Implementation: "Soft diffuse overcast lighting with no harsh shadows. Light is cool neutral gray, even illumination from above."

**Moonlight (月光)**
- Color: Cool blue-white
- Intensity: Low, requires eye adjustment
- Direction: Similar to sunlight but dimmer
- Mood: Mysterious, quiet, intimate
- Implementation: "Cool blue-white moonlight from upper right, creating subtle rim lighting. Shadows are deep blue-gray, not pure black. Overall scene maintains readable mid-tones."

**Firelight (火光)**
- Color: Warm orange-yellow, flickering quality
- Intensity: Medium, localized
- Direction: From source (campfire, candle, lantern)
- Mood: Cozy, primitive, intimate
- Implementation: "Warm orange firelight from lower left, illuminating character's face from below. Light has slight flicker quality. Shadows are warm brown, not black."

### Artificial Light Sources

**Indoor Ceiling Light (室内顶灯)**
- Color: Warm white (incandescent) or cool white (fluorescent/LED)
- Direction: Overhead, even distribution
- Mood: Neutral, everyday, functional
- Implementation: "Even overhead lighting from ceiling fixtures. Warm white tone, minimal shadows, functional illumination."

**Desk Lamp / Task Light (台灯/局部照明)**
- Color: Warm yellow-white
- Direction: Focused, from lamp position
- Intensity: High in lit area, creates strong local contrast
- Mood: Studious, focused, intimate
- Implementation: "Focused warm light from desk lamp on the right, illuminating character's hands and book. Strong contrast between lit area and surrounding dimness."

**Window Light (Indoor) (窗户光)**
- Color: Depends on time of day and weather
- Direction: From window, often creates strong directional light
- Quality: Soft if diffused by curtains, hard if direct
- Mood: Natural, dimensional, atmospheric
- Implementation: "Soft diffused daylight from large window on the left, filtered through sheer curtains. Creates gentle gradient from bright window side to dimmer opposite side."

**Screen Glow (屏幕光)**
- Color: Cool blue-white
- Direction: From screen toward face
- Intensity: Low to medium
- Mood: Modern, isolated, technological
- Implementation: "Cool blue glow from computer screen illuminating character's face from below. Subtle, limited to face and hands, does not overpower other light sources."

**Neon / Colored Artificial Light (霓虹灯/彩色人工光)**
- Color: Saturated (pink, blue, purple, green)
- Direction: From source
- Quality: Often creates colored shadows and reflections
- Mood: Urban, cyberpunk, energetic, artificial
- Implementation: "Pink and blue neon lights from storefronts, creating colored highlights on character's hair and clothing. Shadows have complementary color tints."

## Lighting Setups

### Single Light Source (单光源)

**Most reliable setup for anime illustration models.**

One dominant light source provides all illumination. Shadows are consistent and clear.

**Implementation pattern:**
```
Primary light: [type] from [direction] at [angle]
Shadow behavior: [color and softness]
Fill: Minimal ambient light prevents pure black shadows
```

**Example:**
"Single light source: afternoon sunlight from upper right at 45° angle. Creates warm golden highlights on character's right side. Shadows on left side are cool blue-gray (ambient sky light), soft-edged. No competing light sources."

### Two-Light Setup (双光源)

**Medium risk. Requires careful specification to avoid over-lighting.**

Primary (key) light + secondary (fill or rim) light.

**Safe combinations:**
- Sunlight (key) + sky ambient (fill)
- Window light (key) + room ambient (fill)
- Firelight (key) + moonlight (rim)

**Risky combinations:**
- Two equally strong sources (creates confusing shadows)
- Sources from opposite directions (flattens form)
- More than two colored sources (creates color chaos)

**Implementation pattern:**
```
Primary light: [stronger source] from [direction], provides [X]% of illumination
Secondary light: [weaker source] from [direction], provides [Y]% of illumination, prevents pure black shadows
Shadow behavior: Shadows cast by primary light, softened by secondary
```

**Example:**
"Primary light: warm sunset from left at 30° angle, provides 70% of illumination. Secondary light: cool ambient sky light from above-right, provides 30% fill, prevents black shadows. Shadows are warm brown with soft blue-gray fill."

### Three-Point Lighting (三点布光)

**High risk. Only use if user specifically requests or scene absolutely requires it.**

Key light + fill light + rim/back light.

This is a photography/film technique that often fails in anime illustration because:
- Models struggle with multiple shadow systems
- Over-lighting destroys atmospheric mood
- Complexity increases failure rate

**When it might work:**
- Studio portrait setup (explicitly described as such)
- Character is the only element (no background complexity)
- User has experience and specifically requests it

**Implementation pattern:**
```
Key light: [main source] from [direction], provides primary illumination and shadow definition
Fill light: [soft source] from [opposite side], reduces shadow depth to [X]%
Rim light: [accent source] from [behind], creates edge highlight on [specific areas]
Constraint: Rim light is subtle accent only, does not create second shadow system
```

### Ambient / Overcast Lighting (环境光/漫射光)

**Very safe. No complex shadows.**

Soft, directionless light. Common in overcast outdoor scenes or evenly-lit indoor spaces.

**Implementation pattern:**
```
Lighting: Soft diffuse [color] light from above, no harsh shadows
Shadow behavior: Minimal, soft-edged contact shadows only
Depth cues: Rely on atmospheric perspective and occlusion rather than shadow definition
```

**Example:**
"Soft overcast daylight provides even illumination from above. No harsh shadows, only subtle contact shadows where objects meet surfaces. Light is cool neutral gray. Depth is conveyed through atmospheric perspective rather than shadow contrast."

## Shadow Behavior

### Shadow Color

**Never use pure black shadows in anime illustration.**

Shadows should have color, typically:
- **Outdoor daylight:** Cool blue-gray (ambient sky light)
- **Indoor warm light:** Warm brown or desaturated orange
- **Moonlight:** Deep blue-gray
- **Firelight:** Warm dark brown
- **Colored light:** Complementary color to light source

**Implementation:**
"Shadows are cool blue-gray, not pure black, indicating ambient sky light fill."

### Shadow Softness

**Hard shadows (硬阴影):**
- Sharp edges
- From strong, direct light sources (sun, spotlight)
- Creates dramatic, high-contrast look
- Implementation: "Sharp-edged shadows with clear boundaries"

**Soft shadows (软阴影):**
- Gradual transition from light to shadow
- From diffuse or distant light sources (overcast sky, large window)
- Creates gentle, atmospheric look
- Implementation: "Soft-edged shadows with gradual transition, no harsh boundaries"

**Contact shadows (接触阴影):**
- Darkest where object meets surface
- Present even in soft lighting
- Grounds objects in space
- Implementation: "Subtle contact shadows where feet meet ground, darker directly under character"

### Shadow Density

Specify how dark shadows should be relative to lit areas:

- **High contrast (高对比):** Shadows 70-80% darker than lit areas. Dramatic, graphic look.
- **Medium contrast (中对比):** Shadows 40-60% darker. Balanced, readable.
- **Low contrast (低对比):** Shadows 20-30% darker. Soft, atmospheric, gentle.

**Implementation:**
"Shadows are approximately 50% darker than lit areas, maintaining readable mid-tones throughout the image."

## Common Lighting Scenarios

### Indoor Room with Window (室内窗户光)

**Setup:** Window as primary light source, room ambient as fill.

**Implementation:**
"Primary light from large window on the left, creating soft directional illumination. Window light is diffused by sheer curtains, producing gentle shadows. Room interior provides warm ambient fill light, preventing pure black shadows on the right side. Light gradient from bright window side to dimmer opposite side."

**Risks:**
- Window too bright, room too dark (loses character visibility)
- Multiple windows creating conflicting light directions

**Mitigation:**
"Window provides directional light but room maintains readable mid-tones. Character's face remains clearly visible even on shadow side."

### Night Scene with Moonlight (月光夜景)

**Setup:** Moonlight as primary, minimal ambient to maintain visibility.

**Implementation:**
"Cool blue-white moonlight from upper right at 40° angle, creating rim lighting on character's left side and hair. Shadows are deep blue-gray with enough luminance to show character's expression and clothing details. Overall scene maintains readable mid-tones despite night setting. No pure black areas."

**Risks:**
- Scene too dark, character becomes silhouette
- Over-compensation with too many secondary lights

**Mitigation:**
"Night scene maintains visibility through careful value control. Shadows have color (blue-gray) and sufficient luminance for readability. Moonlight is the only strong light source."

### Sunset/Golden Hour (日落黄金时段)

**Setup:** Low-angle warm light, often as rim/back light.

**Implementation:**
"Low-angle sunset light from behind and to the left, creating warm orange rim lighting on character's silhouette. Face is lit by softer ambient light from the sky, maintaining visibility. Warm-cool contrast between rim light (orange) and fill light (cool blue-gray). Long shadows extend toward camera."

**Risks:**
- Character becomes pure silhouette (loses facial detail)
- Over-saturated orange everywhere

**Mitigation:**
"Sunset provides rim lighting, but character's face receives enough ambient fill light to show expression clearly. Orange tones are concentrated in highlights and rim light, not overall."

### Firelight / Candlelight (火光/烛光)

**Setup:** Warm localized light from below or side.

**Implementation:**
"Warm orange firelight from campfire in lower left, illuminating character's face from below with flickering quality. Light intensity falls off quickly with distance. Shadows are warm brown. Background fades into darkness with minimal visibility. Light creates cozy, intimate atmosphere."

**Risks:**
- Under-lighting from below creates unflattering shadows
- Fire too bright, becomes distracting

**Mitigation:**
"Firelight is warm and present but not harsh. Character's face remains naturally proportioned despite lower light angle. Fire itself is suggested rather than detailed."

### Overcast Outdoor (户外阴天)

**Setup:** Soft diffuse light from above, minimal shadows.

**Implementation:**
"Soft overcast daylight provides even, diffuse illumination. Light is cool neutral gray. No harsh shadows, only subtle contact shadows where character's feet meet ground. Atmosphere is calm and subdued. Depth is conveyed through atmospheric perspective (background slightly desaturated and cooler) rather than shadow contrast."

**Risks:**
- Scene feels flat without shadow definition
- Lack of contrast makes image boring

**Mitigation:**
"Even lighting is balanced with compositional interest and atmospheric depth. Subtle value variations and color temperature shifts create depth without harsh shadows."

## Lighting and Material Interaction

### Translucent Materials (半透明材质)

Materials like fabric, paper, leaves allow light to pass through.

**Implementation:**
"Sunlight passes through character's white dress fabric, creating soft glow and revealing subtle silhouette of legs beneath. Translucency is subtle, limited to thin fabric areas backlit by sun."

**Risk:** Over-application makes everything glow.

**Mitigation:** "Translucency effect only on [specific material] where directly backlit. Other fabrics remain opaque."

### Reflective Materials (反射材质)

Materials like metal, glass, water reflect light sources.

**Implementation:**
"Metal sword reflects warm sunset light as a bright highlight along the blade edge. Reflection is sharp and localized, not diffuse glow."

**Risk:** Everything becomes shiny and reflective.

**Mitigation:** "Reflective highlights only on [specific objects]. Other surfaces are matte."

### Subsurface Scattering (次表面散射)

Light penetrating and scattering within materials like skin, wax, jade.

**Implementation:**
"Backlit ears show subtle warm glow from subsurface scattering, creating soft red-orange translucency. Effect is subtle and limited to thin areas (ears, fingers) where light passes through."

**Risk:** Rarely necessary for anime illustration, often over-applied.

**Mitigation:** Usually skip this unless specifically needed for the aesthetic.

## Atmospheric Effects

### Volumetric Light / God Rays (体积光/丁达尔效应)

Visible light beams through dust, mist, or atmosphere.

**When to use:** Forest scenes, dusty rooms, dramatic moments

**Implementation:**
"Visible sunlight beams stream through window, made visible by dust particles in the air. Beams are subtle, concentrated in the window area, not filling the entire room."

**Risk:** Over-application creates distracting light show.

**Mitigation:** "Light beams are subtle atmospheric accent, limited to [specific area], not dominant visual element."

### Atmospheric Haze (大气雾霾)

Distance creates haze, reducing contrast and shifting color.

**Implementation:**
"Background mountains fade into cool blue-gray atmospheric haze, with reduced detail and contrast. Midground trees retain local color but with lower saturation. Foreground maintains full color saturation and contrast."

**This is a depth cue, not a lighting effect, but often specified together.**

### Lens Flare (镜头光晕)

Optical artifact from bright light hitting camera lens.

**When to use:** Rarely. Anime illustration doesn't need camera artifacts unless specifically going for photographic look.

**If used:**
"Subtle lens flare from sun in upper corner, small and understated, does not obscure character or dominate composition."

**Risk:** Extremely overused by AI models. Usually better to avoid entirely.

**Mitigation:** "No lens flare" or simply don't mention it.

## Lighting Troubleshooting

### Problem: Image is over-lit, everything glows

**Cause:** Too many light sources or effects specified without constraints.

**Solution:**
- Reduce to single primary light source
- Add explicit constraint: "Only [specific object] emits light. All other surfaces are matte and do not glow."
- Specify shadow presence: "Clear shadows indicate single dominant light direction."

### Problem: Shadows are pure black, losing detail

**Cause:** No fill light or ambient light specified.

**Solution:**
- Add shadow color: "Shadows are [color], not pure black"
- Specify ambient fill: "Ambient [source] provides subtle fill light, preventing pure black shadows"
- Set shadow density: "Shadows are [X]% darker than lit areas, maintaining readable detail"

### Problem: Lighting direction is inconsistent

**Cause:** Multiple light sources without clear hierarchy, or vague directional description.

**Solution:**
- Specify single primary source with clear direction: "from upper right at 45° angle"
- If multiple sources, establish hierarchy: "Primary light from [direction] provides 70% of illumination, secondary from [direction] provides 30%"
- Add constraint: "All shadows cast in consistent direction from primary light source"

### Problem: Night scene is too dark to see character

**Cause:** Realistic night lighting doesn't work for illustration readability.

**Solution:**
- Specify readable mid-tones: "Night scene maintains sufficient luminance for character's face and expression to remain clearly visible"
- Use colored shadows instead of black: "Shadows are deep blue-gray, not pure black"
- Add subtle fill: "Ambient starlight/moonlight provides minimal fill to maintain readability"

### Problem: Lighting feels flat despite having shadows

**Cause:** Insufficient contrast or poorly placed light direction.

**Solution:**
- Increase contrast: "Shadows are 50-60% darker than lit areas"
- Use side or three-quarter lighting instead of front lighting
- Add rim light: "Subtle rim light from behind separates character from background"

## Quick Reference: Light Source Selection

| Scene Type | Recommended Light | Avoid |
|------------|------------------|-------|
| Outdoor day | Single sunlight + sky ambient | Multiple competing sources |
| Outdoor night | Moonlight + minimal ambient | Too many artificial lights |
| Indoor day | Window light + room ambient | Overhead + window + lamp |
| Indoor night | Single lamp/ceiling light | Multiple lamps from different directions |
| Dramatic | Single strong directional | Flat front lighting |
| Soft/gentle | Diffuse overcast or large window | Hard spotlight |
| Intimate | Warm localized (fire, lamp) | Bright overhead |
| Mysterious | Rim/back lighting | Full front lighting |

## Integration with Other Layers

Lighting decisions affect:

- **Color:** Light color tints everything it touches
- **Mood:** Light quality (hard/soft, warm/cool) sets emotional tone
- **Depth:** Shadows and atmospheric effects create spatial depth
- **Focus:** Brightest area draws viewer attention
- **Material:** Different materials respond differently to light

Always consider how lighting supports the overall narrative and emotional intent of the illustration.
