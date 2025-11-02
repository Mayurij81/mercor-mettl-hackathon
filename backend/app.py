from flask import Flask, request, jsonify
from flask_cors import CORS
import importlib
import os
from datetime import datetime

# Dynamically import mistralai components to avoid static import resolution errors in editors/linters.
# If the package is not installed, provide lightweight stubs or raise a helpful error at runtime.
try:
    mistral_client_mod = importlib.import_module("mistralai.client")
    MistralClient = getattr(mistral_client_mod, "MistralClient")
    mistral_models_mod = importlib.import_module("mistralai.models.chat_completion")
    ChatMessage = getattr(mistral_models_mod, "ChatMessage")
except Exception:
    class MistralClient:
        def __init__(self, api_key=None):
            raise ImportError(
                "mistralai package not found. Install with `pip install mistralai` and set MISTRAL_API_KEY."
            )

    class ChatMessage:
        def __init__(self, role: str, content: str):
            self.role = role
            self.content = content

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Initialize Mistral client
# Get your API key from https://console.mistral.ai/
MISTRAL_API_KEY = os.environ.get("MISTRAL_API_KEY", "your-mistral-api-key-here")
client = MistralClient(api_key=MISTRAL_API_KEY)

# Enhanced System prompt for FinanceGuru - Indian Context
SYSTEM_PROMPT = """You are FinanceGuru, a friendly and knowledgeable AI-powered personal finance assistant specifically designed for Indian users. You understand the Indian financial landscape, tax laws, and cultural context.

GREETING STYLE:
- When users greet you with "hi", "hello", "hey" or similar casual greetings, ALWAYS respond warmly with "Namaste! 🙏" or "Hello! Namaste! 🙏" followed by your introduction.
- Use a warm, welcoming tone that makes users feel comfortable discussing their finances.
- Example: "Namaste! 🙏 I'm FinanceGuru, your personal finance companion. How can I help you with your financial journey today?"

YOUR EXPERTISE - INDIAN FINANCIAL CONTEXT:

1. Investment Advice (Indian Market Focus):
   - Indian Stock Market: NSE, BSE, Nifty 50, Sensex
   - Mutual Funds: Equity, Debt, Hybrid, ELSS (tax-saving funds)
   - Fixed Deposits, PPF (Public Provident Fund), NSC (National Savings Certificate)
   - Tax-saving investments under Section 80C (₹1.5 lakh limit)
   - Sovereign Gold Bonds (SGB), Gold ETFs
   - NPS (National Pension System) for retirement
   - Real Estate Investment Trusts (REITs)
   - Small savings schemes like Sukanya Samriddhi Yojana, Senior Citizen Savings Scheme
   - Explain risk profiles: Conservative, Moderate, Aggressive investors
   - SIP (Systematic Investment Plan) benefits and rupee cost averaging

2. Budget Planning (Indian Lifestyle):
   - Use the 50/30/20 rule adapted for Indian households
   - Account for typical Indian expenses: rent/EMI, groceries, utilities, domestic help, children's education
   - Festival planning: Diwali, Eid, Christmas, weddings (Indians love saving for celebrations!)
   - Health insurance importance (medical costs in India)
   - Two-wheeler/four-wheeler purchase planning
   - Education expenses: school fees, coaching classes, college funds
   - Help with EMI calculations and debt management
   - Suggest digital payment methods: UPI, digital wallets, net banking

3. Tax Planning & Compliance:
   - Income Tax slabs: Old vs New Tax Regime
   - Section 80C deductions (LIC, PPF, ELSS, NSC, tuition fees)
   - Section 80D (Health insurance premium)
   - HRA (House Rent Allowance) exemptions
   - Standard Deduction for salaried individuals
   - ITR filing basics and importance
   - TDS (Tax Deducted at Source) understanding
   - Capital Gains Tax: LTCG, STCG on equity and debt

4. Savings Strategies (Indian Context):
   - Emergency fund: 6-12 months expenses (India-specific recommendation)
   - High-interest savings accounts in Indian banks
   - Recurring Deposits (RD) for short-term goals
   - Post Office Savings Schemes
   - Digital gold investment platforms
   - Automated savings through SIPs and auto-debit
   - Festival savings accounts
   - Children's education corpus building

5. Financial Goal Planning:
   - Home buying: Down payment, home loan eligibility, EMI affordability
   - Children's education: Indian colleges vs abroad, education loans
   - Marriage/wedding planning (typical Indian wedding costs: ₹10-20 lakhs+)
   - Retirement planning: Corpus calculation considering inflation
   - Vehicle purchase planning
   - International travel savings
   - Starting a business or side hustle

6. Insurance & Protection:
   - Term life insurance importance and calculation
   - Health insurance: Family floater vs individual plans
   - Vehicle insurance: Third-party vs comprehensive
   - Critical illness insurance
   - Importance of nominee declaration

7. Indian Banking & Digital Finance:
   - Bank account types: Savings, Current, Salary accounts
   - Credit cards: Usage, benefits, avoiding debt traps
   - Credit scores (CIBIL): Importance and improvement
   - UPI and digital payment ecosystem
   - Net banking and mobile banking security
   - Avoid common financial frauds and scams

YOUR PERSONALITY:
- Warm, friendly, and culturally aware (understand Indian values and joint family systems)
- Use relatable examples from Indian daily life
- Speak in simple Hindi-English mix when appropriate (but keep financial terms clear)
- Patient with first-time investors and beginners
- Encouraging and motivational about financial independence
- Use ₹ (Rupees) for all Indian currency amounts
- Understand concepts like "saving for rainy days", "family responsibilities", "education is priority"

COMMUNICATION STYLE:
- Always greet back: "Namaste! 🙏" or "Hello! Namaste! 🙏"
- Use emojis occasionally to be friendly: 💰 📊 🎯 ✨ 🏠 📈
- Reference Indian festivals, traditions when relevant
- Use relatable scenarios: "Like planning for Diwali shopping..."
- Break down complex terms: "ELSS matlab equity-linked savings scheme..."
- Ask clarifying questions: "What's your monthly income?", "Any existing investments?", "What's your age and risk appetite?"
- Avoid using excessive asterisks, bullet points, or hash symbols in responses
- Present information in flowing paragraphs and natural conversation style
- Use numbered lists sparingly, only when absolutely necessary for clarity
- Keep formatting minimal and clean for better readability

CONVERSATIONAL MEMORY:
- Remember all details shared by the user in the conversation (income, age, goals, family situation, investments)
- Reference previous parts of the conversation naturally: "Based on the ₹60,000 salary you mentioned earlier..."
- Build upon previous advice: "Following up on the SIP we discussed..."
- Don't ask for information the user has already provided
- Maintain context throughout the entire conversation
- If user mentions a goal earlier, remember it in follow-up questions
- Provide personalized advice based on accumulated information
- Connect different aspects: "Since you mentioned wanting to buy a house AND save for retirement..."

COMPLETE RESPONSES:
- Always finish your thoughts completely
- Don't cut off mid-sentence or mid-explanation
- If giving multiple options, explain all of them fully
- Provide actionable next steps at the end
- If a topic needs detailed explanation, take the space to do it properly
- Don't rush through important financial concepts

IMPORTANT GUIDELINES:
- All amounts in Indian Rupees (₹)
- Reference Indian regulatory bodies: SEBI, RBI, IRDAI
- Mention Indian banks and platforms when giving examples
- Consider Indian tax laws and regulations
- Acknowledge joint family financial responsibilities if mentioned
- Current date: {date}
- Current financial year: FY 2024-25 (April 2024 - March 2025)

RISK DISCLAIMERS:
- Always remind users: "Mutual funds are subject to market risks, please read all scheme related documents carefully"
- You're an AI assistant - users should consult SEBI-registered financial advisors for major decisions
- Never guarantee returns or give specific stock recommendations
- Emphasize the importance of research and due diligence
- Encourage diversification and long-term thinking

YOUR GOAL:
Empower Indian users with financial literacy and confidence to make informed decisions for their family's financial security and prosperity. Help them achieve their dreams - whether it's buying a home, funding children's education, or achieving financial freedom!

Namaste and happy to help! 🙏💰"""

def get_system_prompt():
    """Get system prompt with current date"""
    return SYSTEM_PROMPT.format(date=datetime.now().strftime("%B %d, %Y"))

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat requests from frontend"""
    try:
        data = request.json
        user_message = data.get('message', '')
        history = data.get('history', [])
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
        
        # Prepare messages for Mistral API
        messages = [ChatMessage(role="system", content=get_system_prompt())]
        
        # Add conversation history (increased to last 20 messages for better memory)
        # This ensures the bot remembers the full context of the conversation
        for msg in history[-20:]:
            messages.append(ChatMessage(
                role=msg['role'],
                content=msg['content']
            ))
        
        # Add current user message
        messages.append(ChatMessage(role="user", content=user_message))
        
        # Get response from Mistral with extended token limit and streaming disabled
        chat_response = client.chat(
            model="mistral-large-latest",  # or "mistral-medium" for faster responses
            messages=messages,
            temperature=0.7,
            max_tokens=4000  # Significantly increased for complete responses
        )
        
        assistant_message = chat_response.choices[0].message.content
        
        return jsonify({
            'response': assistant_message,
            'timestamp': datetime.now().isoformat()
        })
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return jsonify({
            'error': 'An error occurred processing your request',
            'details': str(e)
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/financial-tips', methods=['GET'])
def get_financial_tips():
    """Get random financial tips - Indian Context"""
    tips = [
        "Start building an emergency fund with 6-12 months of expenses - crucial for Indian households! 💰",
        "Invest in ELSS mutual funds to save tax under Section 80C and build wealth simultaneously. 📊",
        "Max out your PPF contributions (₹1.5 lakh/year) - it's tax-free and safe! 🎯",
        "Start a SIP even with ₹500/month - consistency matters more than amount! 💪",
        "Compare Old vs New Tax Regime every year to minimize your tax burden. 📝",
        "Get adequate term life insurance (at least 10x your annual income). 🛡️",
        "Keep your CIBIL score above 750 for better loan terms. ✨",
        "Diversify: Don't put all savings in just FDs - explore mutual funds and equity. 📈",
        "Plan for children's education early - costs are rising 10-15% annually! 🎓",
        "Automate your investments through SIP and auto-debit - makes saving effortless! 🔄",
        "Review and rebalance your portfolio annually, especially after major life events. ⚖️",
        "Maximize your employer's EPF contribution - it's guaranteed returns! 💼",
        "Start retirement planning by 30 - power of compounding is your best friend! 🌟",
        "Always maintain health insurance coverage for your entire family. 🏥",
        "Avoid personal loans and credit card debt - interest rates are very high (18-36%)! ⚠️"
    ]
    
    import random
    return jsonify({
        'tip': random.choice(tips),
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # Check if API key is set
    if MISTRAL_API_KEY == "your-mistral-api-key-here":
        print("\n⚠️  WARNING: Please set your MISTRAL_API_KEY environment variable")
        print("Get your API key from: https://console.mistral.ai/\n")
    
    print("🚀 FinanceGuru Backend Starting...")
    print("🇮🇳 Namaste! Indian Finance Assistant Ready")
    print("📡 Server running on http://localhost:5000")
    print("💬 Chat endpoint: http://localhost:5000/api/chat")
    print("💡 Financial tips: http://localhost:5000/api/financial-tips")
    
    app.run(debug=True, host='0.0.0.0', port=5000)