# Ready-made prompts

For people (or agents) without the skill, or when each stage runs in a separate chat. Replace the placeholders in angle brackets.

## 1. Storyboard

```
I want an explainer video about <topic>. The source is <attached file / URL list>.
Using only the source, build a storyboard as Markdown:
- Audience: <who>; after watching they should <think/do what>
- <2-4> minutes per video; split into several if the material is large
- Show <what motion/diagram> in animation
- Use <familiar object> as an analogy
For each scene give approximate seconds, on-screen motion, captions and narration. Do not add numbers or examples that are not in the source; mark illustrations "(example)".
```

## 2. HTML animation

```
Turn this storyboard (<episode 1>) into an animation as a single 16:9 HTML file.
- Mood: like <reference video>
- Canvas 2D, a pure function of time t (same t -> same picture)
- Include the narration lines and fit scene length to the lines; keep the pace brisk
- Provide scene-by-scene preview, duration editing, a timeline, silent MP4 export, and SRT / script TXT export (audio is added later)
```

## 3. Add voice and BGM to a silent video

```
Add English narration (script attached) and subtle background music to the attached silent video.
- Voice: <voice name, calm newsreader style>
- Place each line at its scene; never run over the scene end
- Duck the music under the narration
- Pronunciation: <written> -> <spoken>
- Normalize to -16 LUFS; output H.264 + AAC MP4
```

## 4. From demo recordings

```
The attached <N> recordings form one continuous demo. Look through all of them and write a storyboard that explains the flow in detail.
```
```
Build the matching HTML. Show the demo and add key points and notes on screen in <language>. Label the tools used so viewers understand them.
```
```
Render it to MP4 with audio and background music like <reference video>: no player UI, and the key points and screen state easy to see.
```

## 5. Re-use for another customer/topic

```
Using the attached video (HTML + storyboard) as the template, make episode 0 (3-5 minutes) for <customer/topic>.
1. Research <topic> from the supplied material and public sources and verify key facts in primary sources.
2. Write a storyboard in the same look, with the opening <title + summary / question / conclusion first / ...> and a title card / agenda if wanted, not a feature list.
3. After I approve the storyboard, produce the video with narration and BGM.
It will be shown externally: no confidential data and no private individuals' names.
```

## 6. 3D version (advanced)

```
Recreate the attached explainer video's content as a 3D presentation with Three.js.
```

3D looks richer but can hide the message. Start with 2D.
