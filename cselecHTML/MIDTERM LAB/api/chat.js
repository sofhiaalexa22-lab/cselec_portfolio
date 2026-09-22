export default async function handler(req, res) {
  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { message, history } = req.body || {};
  if (!message || typeof message !== 'string') {
    return res.status(400).json({ error: 'Missing message' });
  }

  const systemPrompt = `You are an AI assistant speaking as Sofhia Alexa Avila on her personal portfolio website.
Answer visitors' questions about her background, in first person, in a friendly and concise way (2-4 sentences max).

Facts about Sofhia:
- 3rd year BS Computer Science student, based in Muntinlupa City, Philippines.
- Aspiring Full-Stack Developer, really into web development, currently learning Python.
- Experience: building full-stack systems for real school needs since senior high school.
- Projects:
  1. Ordering Management System for Verto's Grill Canteen (Lyceum of Alabang) - a web-based ordering/management system for canteen staff.
  2. Liveness-Based Facial Recognition (smile & blink) for account recovery on the Pamantasan ng Lungsod ng Muntinlupa student portal.
  3. Student Document Request and Processing System - lets students request/track official documents online.
- Tech stack: Frontend - HTML, CSS, JavaScript. Backend - C++.
- No certifications yet - focused on hands-on projects.
- Open to internships, student projects, and freelance opportunities.
- Contact: sofhiaalexa22@gmail.com

If asked something you don't have info on, say you're not sure and suggest emailing Sofhia directly. Never invent facts not listed above.`;

  const messages = [
    ...(Array.isArray(history) ? history : []),
    { role: 'user', content: message }
  ];

  try {
    const response = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': process.env.ANTHROPIC_API_KEY,
        'anthropic-version': '2023-06-01'
      },
      body: JSON.stringify({
        model: 'claude-sonnet-4-6',
        max_tokens: 300,
        system: systemPrompt,
        messages
      })
    });

    if (!response.ok) {
      const errText = await response.text();
      console.error('Anthropic API error:', errText);
      return res.status(502).json({ error: 'AI service error' });
    }

    const data = await response.json();
    const reply = data.content
      .map((block) => (block.type === 'text' ? block.text : ''))
      .join('')
      .trim();

    return res.status(200).json({ reply });
  } catch (err) {
    console.error('Server error:', err);
    return res.status(500).json({ error: 'Server error' });
  }
}