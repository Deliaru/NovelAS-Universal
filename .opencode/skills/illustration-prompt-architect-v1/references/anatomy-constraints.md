# Anatomy Constraints for Pose Description

## Purpose

Anime illustration models are trained on diverse art styles with varying anatomical conventions. Without explicit constraints, they may blend incompatible anatomical systems, resulting in:

- Extra or missing limbs
- Impossible joint angles
- Inconsistent proportions
- Floating or disconnected body parts
- Ambiguous weight distribution

This reference provides templates for describing poses with sufficient anatomical constraints to prevent these failures.

## Basic Anatomical Rules

### Limb Count and Symmetry

**Standard human:**
- 1 head
- 1 torso (chest + abdomen)
- 2 arms (upper arm + forearm + hand)
- 2 legs (thigh + calf + foot)
- 2 hands (5 fingers each)
- 2 feet (5 toes each, usually not individually visible)

**When to specify explicitly:**
- Complex poses where limbs might overlap
- Unusual viewing angles
- Multiple characters in close proximity
- Any pose beyond standard standing/sitting

**Template:**
"The character has one complete body with two arms, two legs, two hands (five fingers each), and two feet. All limbs are proportional and symmetric."

### Skeletal Alignment

The human skeleton has three major segments that must align:
1. **Shoulders (肩线)**: Horizontal line connecting shoulder joints
2. **Chest/Ribcage (胸腔)**: Contains spine, determines torso orientation
3. **Pelvis/Hips (骨盆)**: Horizontal line connecting hip joints

**Rule:** These three segments can rotate relative to each other, but their orientations must be anatomically plausible.

**Safe combinations:**
- All three facing same direction (straight-on pose)
- Shoulders rotated 30° from hips (contrapposto, walking)
- Chest twisted 45° from hips (looking back over shoulder)

**Unsafe combinations:**
- Shoulders facing forward, hips facing backward (requires 180° spine twist - impossible)
- Extreme twists without corresponding torso deformation

**Template:**
"Shoulder line, chest, and pelvis are aligned [describe orientation]. Torso shows natural [twist/straight] posture."

### Weight Distribution

Every pose must have clear weight distribution:
- **Standing**: One or both legs bear weight
- **Sitting**: Hips/buttocks bear weight, feet may or may not touch ground
- **Lying**: Body supported along its length
- **Leaning**: Weight transferred to support point (wall, railing, furniture)

**Template:**
"Weight is primarily on [body part/support]. [Primary weight-bearing leg/support] is [straight/slightly bent], [other leg] is [relaxed/bent/extended]."

## Common Poses and Constraints

### Standing Poses

**Standard Standing (标准站姿)**

Safe, reliable pose.

```
Character stands upright with feet shoulder-width apart. Weight is evenly distributed on both feet, which are flat on the ground. Knees are slightly relaxed (not locked). Arms hang naturally at sides or [specific arm position]. Shoulders are level, chest faces forward, hips aligned with shoulders.
```

**Contrapposto (对立式平衡)**

One leg bears weight, other leg relaxed. Creates natural, dynamic standing pose.

```
Character stands with weight on right leg, which is straight and bears full body weight. Left leg is relaxed and slightly bent, with foot resting lightly on ground. This creates a subtle hip tilt - right hip slightly higher than left. Shoulders remain level or tilt slightly opposite to hips (left shoulder slightly higher). Arms [specific position].
```

**Casual Lean (随意倚靠)**

Character leans against wall, railing, or furniture.

```
Character leans back against [support object] with shoulders and upper back making contact. Weight is partially supported by [object], partially on feet. Feet are [distance] from wall base, knees slightly bent. Arms [specific position]. Body forms slight diagonal line from feet to shoulders.
```

### Sitting Poses

**Chair Sitting (椅子坐姿)**

```
Character sits on [chair/bench] with hips and buttocks bearing weight. Feet are flat on ground, knees bent at approximately 90°. Thighs are horizontal, lower legs vertical. Back is [straight/relaxed against backrest]. Arms [specific position - resting on armrests, in lap, etc.].
```

**Floor Sitting - Legs Extended (地面坐姿-伸腿)**

```
Character sits on floor with legs extended forward. Hips and buttocks bear weight. Legs are together/apart, knees straight or slightly bent. Feet point upward or fall naturally to sides. Torso is upright or leans slightly back, supported by [arms behind, leaning on hands]. Arms [specific position].
```

**Floor Sitting - Cross-legged (盘腿坐)**

```
Character sits cross-legged on floor with hips bearing weight. Right leg crosses over left (or vice versa), feet tucked near opposite thighs. Knees point outward and downward. Torso is upright, back straight or slightly curved. Arms [specific position - resting on knees, in lap, etc.].
```

**Seiza (正座)**

Traditional Japanese kneeling sit.

```
Character kneels with shins flat on ground, sitting back on heels. Knees are together or slightly apart. Feet are tucked under buttocks, toes pointing backward. Torso is upright, back straight. Hands rest on thighs or in lap. Weight is distributed between knees, shins, and feet.
```

**Perched Sitting (高处坐姿)**

Sitting on windowsill, desk, railing, etc.

```
Character sits on [elevated surface] with hips bearing weight. Legs dangle freely with feet not touching ground, or one foot rests on surface while other dangles. Knees are bent naturally. Torso is upright or leans slightly. Arms [specific position - gripping edge, resting beside body, etc.]. Balance is maintained through hip placement and possibly hand support.
```

### Reclining Poses

**Lying on Back (仰卧)**

```
Character lies on back on [surface]. Full length of back, from shoulders to hips, makes contact with surface. Head rests on [surface/pillow]. Legs are [extended straight, bent at knees, one bent one straight]. Arms are [at sides, folded on chest, behind head, etc.]. Body is fully supported by surface.
```

**Lying on Side (侧卧)**

```
Character lies on [left/right] side on [surface]. Shoulder, hip, and leg of lower side make contact with surface. Head rests on [lower arm, pillow, hand]. Upper leg is [extended along lower leg, bent with knee forward]. Upper arm is [resting on upper side, propped on elbow, extended forward]. Body forms gentle curve.
```

**Lying on Stomach (俯卧)**

```
Character lies face-down on [surface]. Chest, stomach, and front of legs make contact with surface. Head is [turned to side, resting on arms, propped up on elbows]. Legs are [extended straight, bent at knees with feet up]. Arms are [extended forward, folded under head, propped for support].
```

### Dynamic Poses

**Walking (行走)**

```
Character is mid-stride. Left leg is forward with foot flat on ground, knee slightly bent, bearing weight. Right leg is behind with foot pushing off ground, heel raised, toes still in contact. Arms swing naturally in opposition - right arm forward, left arm back. Torso faces forward with slight rotation toward weight-bearing leg. Shoulders and hips show natural counter-rotation.
```

**Running (奔跑)**

```
Character is mid-run. Right leg is forward and bent, foot about to contact ground. Left leg is behind and extended, foot off ground. Arms are bent at elbows, pumping in opposition to legs - left arm forward, right arm back. Torso leans slightly forward. Hair and clothing show motion in direction opposite to movement. Both feet are not on ground simultaneously (flight phase).
```

**Reaching Up (向上伸手)**

```
Character reaches upward with right arm fully extended above head, hand open and fingers spread. Left arm is [at side, partially raised]. Torso stretches upward, spine elongated. Character may be on tiptoes with heels raised, or feet flat on ground. Weight is balanced on both feet. Shoulder of reaching arm is elevated, other shoulder remains level.
```

**Crouching (蹲伏)**

```
Character crouches low with knees deeply bent. Feet are flat on ground, shoulder-width apart. Hips are lowered close to heels. Torso leans forward to maintain balance. Arms are [between knees, resting on knees, extended forward for balance]. Weight is distributed across both feet. Heels remain on ground (full squat) or may be raised (crouch on balls of feet).
```

## Hand and Arm Positions

Hands are notoriously difficult for AI models. Provide explicit constraints.

### Safe Hand Positions

**Hands at sides:**
"Arms hang naturally at sides with hands relaxed, fingers slightly curved, palms facing inward toward thighs."

**Hands clasped:**
"Hands are clasped together in front of body, fingers interlaced. Both hands are clearly visible with correct finger count (five per hand)."

**Hands in pockets:**
"Hands are inserted into pockets with only wrists visible. Fingers are hidden inside pockets." (Safest option - avoids drawing hands entirely)

**Hands holding object:**
"Right hand holds [object] with fingers wrapped around it naturally. Thumb is on one side, four fingers on the other. Hand shows natural grip with slight finger bend."

**Hands resting on surface:**
"Hands rest flat on [table/lap/knees] with palms down, fingers extended and relaxed. All five fingers of each hand are visible and naturally spaced."

### Risky Hand Positions (Use with Caution)

**Pointing:**
"Right hand points forward with index finger extended, other three fingers curled into palm, thumb relaxed. Hand has one extended finger, three curled fingers, one thumb - five digits total."

**Peace sign / Victory sign:**
"Right hand makes V-sign with index and middle fingers extended and separated, other two fingers curled into palm, thumb holding them. Hand shows two extended fingers, two curled fingers, one thumb - five digits total."

**Interlaced fingers (complex):**
"Hands are clasped with fingers interlaced. Each hand has five fingers. Fingers alternate between hands in the interlacing pattern."

**Touching face:**
"Right hand touches face with fingertips resting gently on cheek. Fingers are slightly curved, palm faces toward face. Hand has five fingers, all visible or partially visible."

### When to Avoid Showing Hands

If the pose is already complex, consider hiding hands:
- In pockets
- Behind back
- Holding object that obscures fingers
- Out of frame
- Covered by sleeves or other objects

**Template:**
"Hands are [hidden in pockets / behind back / out of frame], avoiding the need to render complex finger details."

## Foot and Leg Positions

### Safe Foot Positions

**Standing flat:**
"Both feet are flat on ground, shoulder-width apart, toes pointing forward. Feet show natural contact with ground plane."

**One foot raised:**
"Left foot is flat on ground bearing weight. Right foot is raised with toes resting lightly on ground, heel elevated. Right leg is relaxed and slightly bent."

**Sitting with feet on ground:**
"Feet are flat on ground, positioned below knees. Ankles are at natural 90° angle, no hyperextension."

**Feet hidden:**
"Feet are hidden [under long skirt / behind furniture / out of frame]." (Safest option)

### Risky Foot Positions

**Tiptoes:**
"Character stands on tiptoes with heels raised high, weight on balls of feet. Ankles are extended but not hyperextended. Calves are tensed."

**Crossed legs (standing):**
"Right leg crosses in front of left at ankle level. Left foot is flat on ground bearing most weight. Right foot rests lightly with toes touching ground."

**Complex sitting positions:**
Avoid unless necessary. If required, be very explicit about which leg is where.

## Interaction Between Characters

When multiple characters interact, anatomical constraints become critical.

### Safe Interactions

**Standing side-by-side:**
"Two characters stand side-by-side, [distance] apart. Each character has independent, clear pose. No physical contact. Each character's limbs are clearly distinguishable and belong to their own body."

**One character behind another:**
"Character A stands in foreground, fully visible. Character B stands behind Character A, partially obscured. Only Character B's [head and shoulders / upper body] is visible above/beside Character A. Each character maintains independent anatomical structure."

### Medium Risk Interactions

**Hand on shoulder:**
"Character A places right hand on Character B's left shoulder. Character A's arm extends from their own body, crosses the space between them, and makes contact with Character B's shoulder. Hand has five fingers. Character B's body remains independent with their own two arms clearly visible."

**Holding hands:**
"Character A's right hand holds Character B's left hand. Hands are clasped with fingers interlaced or palms pressed together. Each hand has five fingers. Arms extend from their respective bodies to the point of contact. Each character maintains their own independent body structure."

### High Risk Interactions (Avoid Unless Necessary)

**Hugging:**
Very difficult for models. If required:
"Character A and Character B embrace. Character A's arms wrap around Character B's back. Character B's arms wrap around Character A's shoulders. Each character has two arms, two hands. Arms do not multiply or merge. Bodies are close but each character maintains independent structure with their own torso, head, and legs."

**Carrying/lifting:**
Extremely difficult. Consider alternative compositions.

**Fighting/complex contact:**
Extremely difficult. Consider showing before/after moment rather than contact moment.

## Troubleshooting Common Failures

### Problem: Extra limbs appear

**Cause:** Overlapping body parts or ambiguous pose description

**Solution:**
- Add explicit limb count: "Character has exactly two arms and two legs"
- Describe each limb's position individually: "Right arm [position], left arm [position]"
- Avoid ambiguous phrasing like "arms raised" (which arms? how many?)

### Problem: Limbs at impossible angles

**Cause:** Insufficient joint constraints

**Solution:**
- Specify joint angles: "Elbow bent at approximately 90°"
- Add natural range constraint: "Arm bends naturally at elbow, no hyperextension"
- Reference real human capability: "Pose is within natural human range of motion"

### Problem: Floating or disconnected body parts

**Cause:** Unclear connection to body or ground

**Solution:**
- Specify attachment points: "Arm extends from shoulder"
- Describe ground contact: "Feet are flat on ground with clear contact"
- Add weight distribution: "Weight is supported by [specific body part]"

### Problem: Inconsistent proportions

**Cause:** No proportion reference

**Solution:**
- Add proportion constraint: "Limbs are proportional to body"
- Specify relative sizes: "Arms reach to mid-thigh when hanging at sides"
- Reference standard proportions: "Character has natural human proportions"

## Quick Reference: Constraint Templates

### Minimal Constraint (Simple Poses)

"Character [stands/sits] with natural posture. Arms and legs are positioned naturally. Body proportions are consistent."

### Standard Constraint (Most Poses)

"Character has one complete body with two arms, two legs, two hands (five fingers each), and two feet. [Specific pose description]. Weight is [distribution]. Limbs are proportional and joints bend naturally."

### Maximum Constraint (Complex Poses)

"Character has exactly one body with two arms, two legs, two hands (five fingers each), and two feet. Shoulder line, chest, and pelvis are aligned [orientation]. Right arm [specific position], left arm [specific position]. Right leg [specific position], left leg [specific position]. Weight is primarily on [support]. All joints bend within natural human range. No extra limbs, no hyperextended joints, no impossible angles. Limbs are proportional and symmetric."

## Integration into Prompts

Anatomical constraints go in the **action layer** of the prompt, immediately after describing the pose:

```
[Character description...]

Character [pose description with specific positions]. [Anatomical constraints appropriate to pose complexity]. [Weight distribution and ground contact].

[Camera, environment, style layers...]
```

**Example:**

"Character sits on a wooden bench with her right leg bent and foot resting on the bench, left leg dangling naturally with foot not touching ground. She has one complete body with two arms and two legs. Her right arm wraps around her bent right knee, left arm rests on the bench beside her. Weight is supported by her hips on the bench surface. Limbs are proportional, joints bend naturally."

## Final Note

The goal is not to write a medical anatomy textbook, but to provide enough constraints that the model doesn't generate anatomical impossibilities. Match constraint level to pose complexity:

- **Simple pose** (standing, sitting normally): Minimal constraints
- **Moderate pose** (reaching, leaning, casual): Standard constraints
- **Complex pose** (dynamic action, unusual angle, interaction): Maximum constraints

When in doubt, add more constraints rather than fewer. It's easier to be explicit than to fix anatomical failures after generation.
