# mock_data.py
#
# This file holds all of our "fake" research data.
# In a real AI Research Agent, this data would come from:
#   - a web search API (like Google/Bing/Tavily search)
#   - an AI model (like Claude) reading and summarizing pages
#
# For this demo version, we simply store ready-made research
# information as Python dictionaries and lists. The research_agent.py
# file reads from here instead of calling any real API.

# Each topic below is a dictionary with the same structure, so the
# rest of the app can treat every topic the same way.
TOPICS = {
    "artificial intelligence": {
        "display_name": "Artificial Intelligence",
        "research_questions": [
            "What is artificial intelligence and how does it work?",
            "How is AI currently being used across industries?",
            "What are the main risks and limitations of AI systems?",
        ],
        "sources": [
            {
                "name": "Example Technology Research Journal",
                "topic": "Foundations of Artificial Intelligence",
                "summary": (
                    "A demo overview explaining how AI systems learn patterns "
                    "from data and use them to make predictions or decisions."
                ),
                "url": "https://demo-source.example.com/ai-foundations",
            },
            {
                "name": "Demo Industry Insights Report",
                "topic": "AI Adoption Across Industries",
                "summary": (
                    "A demo report describing how healthcare, finance, and "
                    "retail sectors are experimenting with AI-driven tools."
                ),
                "url": "https://demo-source.example.com/ai-industry-adoption",
            },
            {
                "name": "Sample Ethics in Computing Review",
                "topic": "Risks and Limitations of AI",
                "summary": (
                    "A demo summary discussing bias, transparency, and safety "
                    "concerns that come with deploying AI systems."
                ),
                "url": "https://demo-source.example.com/ai-ethics",
            },
            {
                "name": "Demo Future Trends Bulletin",
                "topic": "The Future of AI Research",
                "summary": (
                    "A demo article outlining predicted developments in AI "
                    "over the next decade, based on current research trends."
                ),
                "url": "https://demo-source.example.com/ai-future-trends",
            },
        ],
        "key_findings": [
            "AI systems learn patterns from large amounts of data rather than following fixed rules.",
            "Adoption is growing quickly in healthcare, finance, and customer service.",
            "Bias and lack of transparency remain major open challenges.",
            "Regulation and governance of AI are still evolving worldwide.",
        ],
        "themes": [
            "Data-driven learning is the foundation of modern AI.",
            "Real-world adoption is outpacing public understanding of AI.",
            "Trust, safety, and ethics are recurring concerns across sources.",
        ],
        "benefits": [
            "Automates repetitive tasks, freeing up human time.",
            "Can process and analyze data far faster than humans.",
            "Enables new products and services that were previously impossible.",
        ],
        "challenges": [
            "AI models can inherit bias present in their training data.",
            "Many AI systems are difficult to interpret or explain.",
            "High computing costs limit access for smaller organizations.",
        ],
        "gaps": [
            "Long-term societal effects of widespread AI use are not yet well understood.",
            "Standardized methods for measuring AI fairness are still developing.",
        ],
        "contradictions": [
            "Some sources view AI as mainly beneficial for productivity, while others "
            "emphasize job displacement risks, showing no clear consensus yet.",
        ],
    },
    "generative ai": {
        "display_name": "Generative AI",
        "research_questions": [
            "What is generative AI and how is it different from traditional AI?",
            "What are common applications of generative AI today?",
            "What ethical questions does generative AI raise?",
        ],
        "sources": [
            {
                "name": "Demo AI Systems Quarterly",
                "topic": "How Generative Models Work",
                "summary": (
                    "A demo explanation of how generative models learn to produce "
                    "new text, images, or audio based on training examples."
                ),
                "url": "https://demo-source.example.com/genai-basics",
            },
            {
                "name": "Sample Creative Tools Review",
                "topic": "Generative AI in Creative Industries",
                "summary": (
                    "A demo case study on how generative AI is used for writing, "
                    "art, music, and design assistance."
                ),
                "url": "https://demo-source.example.com/genai-creative",
            },
            {
                "name": "Demo Enterprise Technology Digest",
                "topic": "Generative AI in Business",
                "summary": (
                    "A demo article covering how companies use generative AI for "
                    "drafting content, coding assistance, and customer support."
                ),
                "url": "https://demo-source.example.com/genai-business",
            },
            {
                "name": "Example Policy and Ethics Brief",
                "topic": "Ethical Concerns of Generative AI",
                "summary": (
                    "A demo brief discussing copyright, misinformation, and "
                    "authenticity concerns raised by generative AI content."
                ),
                "url": "https://demo-source.example.com/genai-ethics",
            },
        ],
        "key_findings": [
            "Generative AI can create new text, images, audio, and code from learned patterns.",
            "Businesses increasingly use it for content drafting and coding assistance.",
            "Copyright and originality questions remain largely unresolved.",
            "Quality and accuracy of generated content still require human review.",
        ],
        "themes": [
            "Generative AI is shifting from novelty to everyday workplace tool.",
            "Human oversight remains essential for accuracy and quality control.",
            "Legal and ethical frameworks are lagging behind the technology.",
        ],
        "benefits": [
            "Speeds up content creation and brainstorming.",
            "Lowers the barrier to entry for creative and technical work.",
            "Can personalize content at scale.",
        ],
        "challenges": [
            "Generated content can be factually incorrect or misleading.",
            "Questions remain about ownership of AI-generated work.",
            "Risk of overreliance without human verification.",
        ],
        "gaps": [
            "Clear industry standards for labeling AI-generated content are still missing.",
            "Long-term impact on creative professions is not yet well studied.",
        ],
        "contradictions": [
            "Some sources describe generative AI as empowering creators, while others "
            "warn it may devalue original creative work.",
        ],
    },
    "ai in software engineering": {
        "display_name": "AI in Software Engineering",
        "research_questions": [
            "How is AI changing the software development process?",
            "Which parts of the software engineering lifecycle benefit most from AI?",
            "What risks come with using AI-assisted coding tools?",
        ],
        "sources": [
            {
                "name": "Demo Developer Productivity Report",
                "topic": "AI Coding Assistants",
                "summary": (
                    "A demo report on how AI-based code completion tools affect "
                    "developer speed and productivity."
                ),
                "url": "https://demo-source.example.com/ai-coding-assistants",
            },
            {
                "name": "Example Software Quality Journal",
                "topic": "AI in Testing and Debugging",
                "summary": (
                    "A demo summary of how AI tools help generate tests and "
                    "detect potential bugs before deployment."
                ),
                "url": "https://demo-source.example.com/ai-testing",
            },
            {
                "name": "Sample Engineering Practices Review",
                "topic": "AI in Code Review",
                "summary": (
                    "A demo overview describing how AI assists with automated "
                    "code review suggestions and style consistency checks."
                ),
                "url": "https://demo-source.example.com/ai-code-review",
            },
            {
                "name": "Demo Tech Careers Bulletin",
                "topic": "Impact of AI on Developer Roles",
                "summary": (
                    "A demo article exploring how developer responsibilities may "
                    "shift as AI tools take on more routine coding tasks."
                ),
                "url": "https://demo-source.example.com/ai-developer-roles",
            },
        ],
        "key_findings": [
            "AI coding assistants can noticeably speed up writing boilerplate code.",
            "AI tools are increasingly used for generating unit tests and finding bugs.",
            "Code review is being augmented, not replaced, by AI suggestions.",
            "Developer roles are shifting toward reviewing and guiding AI output.",
        ],
        "themes": [
            "AI is becoming a coding collaborator rather than a full replacement.",
            "Productivity gains are strongest on repetitive or boilerplate tasks.",
            "Human judgment remains critical for architecture and design decisions.",
        ],
        "benefits": [
            "Reduces time spent on repetitive coding tasks.",
            "Helps catch bugs earlier through AI-assisted testing.",
            "Supports developers learning new languages or frameworks faster.",
        ],
        "challenges": [
            "AI-suggested code can contain subtle bugs or security issues.",
            "Over-reliance may weaken developers' fundamental coding skills.",
            "Integrating AI tools into existing workflows takes time and training.",
        ],
        "gaps": [
            "Long-term effects on software quality and maintainability are still unclear.",
            "Best practices for safely reviewing AI-generated code are still emerging.",
        ],
        "contradictions": [
            "Some sources report major productivity boosts from AI tools, while "
            "others caution the gains are smaller once debugging AI mistakes is included.",
        ],
    },
    "cybersecurity": {
        "display_name": "Cybersecurity",
        "research_questions": [
            "What are the most common cybersecurity threats today?",
            "How are organizations defending against modern cyber attacks?",
            "What role does AI play in cybersecurity, both offense and defense?",
        ],
        "sources": [
            {
                "name": "Demo Threat Intelligence Digest",
                "topic": "Common Cyber Threats",
                "summary": (
                    "A demo summary of common attack types such as phishing, "
                    "ransomware, and social engineering."
                ),
                "url": "https://demo-source.example.com/cyber-threats",
            },
            {
                "name": "Example Enterprise Security Journal",
                "topic": "Organizational Defense Strategies",
                "summary": (
                    "A demo overview of how organizations use firewalls, monitoring, "
                    "and employee training to reduce security risks."
                ),
                "url": "https://demo-source.example.com/cyber-defense",
            },
            {
                "name": "Sample AI and Security Review",
                "topic": "AI in Cybersecurity",
                "summary": (
                    "A demo article on how AI is used to detect unusual activity, "
                    "while also being used by attackers to craft more convincing attacks."
                ),
                "url": "https://demo-source.example.com/ai-cybersecurity",
            },
            {
                "name": "Demo Compliance and Risk Bulletin",
                "topic": "Cybersecurity Regulations",
                "summary": (
                    "A demo brief covering how data protection regulations shape "
                    "organizational cybersecurity requirements.",
                ),
                "url": "https://demo-source.example.com/cyber-regulation",
            },
        ],
        "key_findings": [
            "Phishing remains one of the most common entry points for cyber attacks.",
            "Organizations are increasingly investing in continuous security monitoring.",
            "AI is used both to detect threats and, unfortunately, to create more convincing attacks.",
            "Regulatory requirements are pushing companies toward stronger data protection.",
        ],
        "themes": [
            "Cybersecurity is shifting from reactive defense to continuous monitoring.",
            "AI is a double-edged sword for both defenders and attackers.",
            "Human error remains a leading cause of security incidents.",
        ],
        "benefits": [
            "AI-powered monitoring can detect unusual activity faster than manual review.",
            "Automated defenses reduce response time during active incidents.",
            "Regulations encourage stronger baseline security practices.",
        ],
        "challenges": [
            "Attackers are also adopting AI to craft more convincing phishing attempts.",
            "Security tooling can be costly for smaller organizations.",
            "Employee awareness training is difficult to maintain consistently.",
        ],
        "gaps": [
            "Standardized methods for measuring real-world security effectiveness are limited.",
            "Long-term impact of AI-driven attacks is still being studied.",
        ],
        "contradictions": [
            "Some sources argue AI defense tools outpace AI-driven attacks, while "
            "others believe attackers currently have the advantage.",
        ],
    },
    "renewable energy": {
        "display_name": "Renewable Energy",
        "research_questions": [
            "What are the main types of renewable energy in use today?",
            "What challenges slow down renewable energy adoption?",
            "How does renewable energy compare to fossil fuels in cost and impact?",
        ],
        "sources": [
            {
                "name": "Demo Clean Energy Report",
                "topic": "Types of Renewable Energy",
                "summary": (
                    "A demo overview of solar, wind, hydro, and geothermal energy "
                    "as leading renewable energy sources."
                ),
                "url": "https://demo-source.example.com/renewable-types",
            },
            {
                "name": "Example Infrastructure Journal",
                "topic": "Renewable Energy Adoption Challenges",
                "summary": (
                    "A demo summary of the infrastructure, storage, and cost "
                    "challenges facing renewable energy adoption."
                ),
                "url": "https://demo-source.example.com/renewable-challenges",
            },
            {
                "name": "Sample Climate Economics Review",
                "topic": "Cost Comparison with Fossil Fuels",
                "summary": (
                    "A demo article comparing the long-term cost trends of "
                    "renewable energy versus traditional fossil fuels."
                ),
                "url": "https://demo-source.example.com/renewable-cost",
            },
            {
                "name": "Demo Policy and Environment Bulletin",
                "topic": "Government Policy on Renewable Energy",
                "summary": (
                    "A demo brief on how government incentives and policy "
                    "decisions influence renewable energy growth."
                ),
                "url": "https://demo-source.example.com/renewable-policy",
            },
        ],
        "key_findings": [
            "Solar and wind power costs have dropped significantly over the past decade.",
            "Energy storage remains a key challenge for reliable renewable supply.",
            "Government incentives play a major role in renewable energy adoption rates.",
            "Renewable energy is increasingly cost-competitive with fossil fuels.",
        ],
        "themes": [
            "Falling costs are accelerating renewable energy adoption worldwide.",
            "Storage and grid infrastructure are the next major hurdles.",
            "Policy support strongly influences the pace of adoption.",
        ],
        "benefits": [
            "Reduces greenhouse gas emissions compared to fossil fuels.",
            "Increasingly cost-competitive with traditional energy sources.",
            "Creates new jobs in manufacturing, installation, and maintenance.",
        ],
        "challenges": [
            "Energy storage technology is still catching up to generation capacity.",
            "Existing power grids often need upgrades to handle renewable sources.",
            "Weather-dependent generation can create supply inconsistency.",
        ],
        "gaps": [
            "Long-term recycling solutions for solar panels and batteries are still developing.",
            "Global adoption rates vary widely, and reasons for the gap need more study.",
        ],
        "contradictions": [
            "Some sources project renewables will fully replace fossil fuels within decades, "
            "while others believe a mixed energy approach will persist much longer.",
        ],
    },
}


def get_generic_topic_data(topic_text):
    """
    Build a generic demo research dataset for any topic that is not
    in our TOPICS dictionary above. This keeps the app from crashing
    or feeling broken when someone enters an unusual topic.
    """
    return {
        "display_name": topic_text.title(),
        "research_questions": [
            f"What is {topic_text} and why does it matter?",
            f"What are the current trends related to {topic_text}?",
            f"What challenges or open questions exist around {topic_text}?",
        ],
        "sources": [
            {
                "name": "Demo General Research Digest",
                "topic": f"Overview of {topic_text.title()}",
                "summary": (
                    f"A demo summary introducing the basic concepts behind "
                    f"'{topic_text}' for general audiences."
                ),
                "url": "https://demo-source.example.com/general-overview",
            },
            {
                "name": "Sample Industry Trends Report",
                "topic": f"Trends in {topic_text.title()}",
                "summary": (
                    f"A demo report describing recent developments and "
                    f"growing interest in '{topic_text}'."
                ),
                "url": "https://demo-source.example.com/general-trends",
            },
            {
                "name": "Example Analysis Bulletin",
                "topic": f"Challenges Related to {topic_text.title()}",
                "summary": (
                    f"A demo bulletin discussing common obstacles and open "
                    f"questions connected to '{topic_text}'."
                ),
                "url": "https://demo-source.example.com/general-challenges",
            },
        ],
        "key_findings": [
            f"'{topic_text.title()}' is an active area of interest with growing discussion.",
            "Multiple perspectives exist, and expert opinions are still developing.",
            "Further real-world research would be needed for a complete picture.",
        ],
        "themes": [
            f"Interest in {topic_text} appears to be increasing over time.",
            "Sources suggest both opportunities and open challenges.",
        ],
        "benefits": [
            f"Understanding {topic_text} may open new opportunities or insights.",
            "Early awareness can help with better decision-making.",
        ],
        "challenges": [
            f"Limited demo data is available specifically for '{topic_text}'.",
            "Real research would require live sources and expert review.",
        ],
        "gaps": [
            f"Deeper, real-world research on '{topic_text}' is recommended.",
            "This demo cannot verify facts, since it uses only local sample data.",
        ],
        "contradictions": [
            "No specific contradictions available in demo data for this topic.",
        ],
    }


def find_topic_data(user_topic):
    """
    Look up demo research data for the topic the user typed in.
    Matching is done by checking if any known topic keyword appears
    inside the user's text (case-insensitive). If nothing matches,
    we fall back to a generic response so the app never crashes.
    """
    cleaned_topic = user_topic.strip().lower()

    # First, try an exact or partial match against our known topics.
    for topic_key, topic_data in TOPICS.items():
        if topic_key in cleaned_topic or cleaned_topic in topic_key:
            return topic_data

    # No match found, so build a generic demo response instead.
    return get_generic_topic_data(user_topic.strip())
