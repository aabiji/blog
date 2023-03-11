# First principles and abstractions

When writing the markdown compiler I use for this blog, I was faced with the problem of 
parsing the markdown into an AST than I could then output as html. But, I'm not joking when I tell you 
that I quite literally struggled for days on end to 
implement it. So you could imagine how clever I felt when I finally figured it out. 
And then how dumb I felt when I realized that what I came up with was 
essentially just recursive descent parsing in a nutshell.

---

I think recursive descent parsing can be best illustrated with an example. 
Say you needed to parse a paragraph. 
At first glance, this may seem really hard because a paragraph seems like an opaque entity with a 
lot of nuances. So you start thinking ... what's a paragraph anyways? Well, a paragraph is just a 
bunch of sentences. Then okay, what's a sentence? Well, a sentence is just a bunch of words and 
grammatical symboles. So, focusing on words, what's a word? Well, a word is just a bunch of 
characters. And the same thing applies to grammatical symboles as well \- they're also just characters. 
So, in a way, to parse a word, you need to just parse a bunch of characters. 
\(Which you probably should have already done in your lexer.\) Then, to parse a sentence, 
you just need to parse a bunch of words and grammatical symboles. Then finally to parse a paragraph, 
you just need to parse a bunch of sentences. You could even extend it further and say to parse a 
text, you'll just parse a bunch of paragraphs. As you can see, the seemingly hard problem actually 
becomes really trivial.

---

Now, obviously parsing a paragraph isn't a quasi NP hard problem to sweat over, but 
in my opinion, recusrive descent parsing is a really good example 
of first principles thinking. Sounds fancy and such, 
but it's really just breaking a problem down to its bare essentials. 
And so, naturally, the reverse of 
that would be coming up with abstractions of how things operate. And so, thinking about it 
that way, you realize that most of computation is built on a series of abstractions. Whether it 
be in a really large codebase or in a complex system like a computer, its in all the abstractions 
that a wide range of people can make progress on different layers of the abstraction stack that 
interests them. Progress that the community at large, including themselves benefit from. 

---

It's really interesting, figuring out how things actually work by breaking down the 
abstractions, and along this the way accidently reinventing the wheel...
