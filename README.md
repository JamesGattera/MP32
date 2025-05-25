# MP32
Micropython and C++ experiments on my ailing PicoW and 'brand new' ESP32(clone), it has an OLED screen :D


17:54/23/05/25
Personal issues related to burnout and overproduction; Managed to open a bag of rotary encoders and learn about their pins.
Will hopefully Put those to use in my next test projests and definitions.

--

0451/24/05/2025
-

Today's contribution is another note, though a little longer;
My major focus behind this project is to make a working radio- I have parts in the post, on their way to me, most of which I'll be learning to use and apply as they arrive. This motivation came from over-playing Stalker GAMMA wherein, I found myself enjoying the simplicity of scrolling through MHz frequencies and tracking down hidden packages as a reward for my continued service to factions. I see myself -one day soon- holding a similar RF reciever of my own design, tuning in to commercial radio, or perhaps hearing something 'I shouldnt' on undescovered bands...

There's a charming secrecy to the kind of communication you can't see.
I look forward to hearing it, to learning how it works on a deeper level.

That said, Today's focus MUST be nutrition - I can't invent or create without fuel.

PS; I've used new jumper wires (the type that sit flat against the breadboard) to properly connect pins-to-micro. I worry this inspiration won't resume once I recover... Consistency is key.

--

PSS: Present bill of materials, minus postage;

-A knock-off ESP32-WROOM-32 with a tacked-on 128/64 OLED.
12 (I was probably ripped off).

-A two-buck breadboard.
2.

-Compartmentalised box of jumper wires.
5.

-A bag of Rotary Encoders.
5.

Making 24 quid?
30 with postage no-doubt...


0414/25/05/25
-

Every example of a rotary encoder I've found illustrates a 'pulse' as a two-button press.
It's taken me this long to realise i don't need state tables (confusing), or hexcode(VERY confusing).
Only two states matter; A-Down, or B-Down.
I didn't sleep much so I could be mad.
Rotary.py to follow.

(PS, I've just learned that dashes with a blank line cause an underline here. Edited for correct emphasis- log dates.)
