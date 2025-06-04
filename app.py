import streamlit as st
import openai
import os
from pathlib import Path

# Configure page layout
st.set_page_config(layout="wide", page_title="ICH+ AI Proposal Generator")

# Load OpenAI API key
def load_api_key():
    return st.secrets["openai_api_key"]

api_key = load_api_key()
if api_key:
    openai.api_key = api_key
else:
    st.error("OpenAI API key not found. Please check the config/openai_api_key file.")
    st.stop()

# Custom CSS for styling
st.markdown("""
<style>
    .main-container {
        background-color: #f8f9fa;
    }
    .stButton button {
        background-color: #6a0dad;
        color: white;
        border-radius: 20px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    .stButton button:hover {
        background-color: #5a0b9a;
        transform: translateY(-2px);
    }
    .persona-card {
        background-color: #f0e6ff;
        border-radius: 15px;
        padding: 20px;
        margin: 10px 0;
        border: 2px solid #d4b3ff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        min-height: 200px;
    }
    .persona-title {
        color: #6a0dad;
        font-size: 1.2em;
        font-weight: bold;
        margin-bottom: 15px;
        text-align: center;
        border-bottom: 2px solid #d4b3ff;
        padding-bottom: 10px;
    }
    .keyword-badge {
        background-color: #d4b3ff;
        color: #6a0dad;
        padding: 8px 15px;
        border-radius: 20px;
        display: inline-block;
        margin: 5px;
        font-weight: bold;
        text-align: center;
        width: 100%;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    .proposal-card {
        background-color: #f0e6ff;
        border-radius: 15px;
        padding: 15px;
        margin: 10px 0;
        border: 2px solid #d4b3ff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        min-height: 120px;
    }
    .highlighted-text {
        background-color: #d4b3ff;
        padding: 2px 5px;
        border-radius: 5px;
        font-weight: bold;
    }
    .chat-message {
        background-color: white;
        padding: 10px;
        border-radius: 10px;
        margin: 5px 0;
        border-left: 4px solid #6a0dad;
    }
    .section-header {
        color: #6a0dad;
        font-size: 1.5em;
        font-weight: bold;
        margin: 30px 0 20px 0;
        text-align: center;
        border-bottom: 3px solid #6a0dad;
        padding-bottom: 10px;
    }
    .input-section {
        background-color: white;
        padding: 30px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin: 20px 0;
        text-align: center;
    }
    .app-title {
        color: #6a0dad;
        font-size: 2.5em;
        font-weight: bold;
        text-align: center;
        margin-bottom: 10px;
    }
    .app-subtitle {
        color: #666;
        font-size: 1.2em;
        text-align: center;
        margin-bottom: 30px;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'generated_keywords' not in st.session_state:
    st.session_state['generated_keywords'] = []
if 'selected_keyword' not in st.session_state:
    st.session_state['selected_keyword'] = None
if 'proposals' not in st.session_state:
    st.session_state['proposals'] = {}
if 'selected_proposal' not in st.session_state:
    st.session_state['selected_proposal'] = None
if 'show_personas' not in st.session_state:
    st.session_state['show_personas'] = False
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = {"art_creator": [], "art_collector": [], "art_appreciator": []}

# Function to interact with GPT-4o-mini
def get_ai_response(prompt, persona):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": f"You are an AI assistant specializing in intangible cultural heritage art. You are talking to a {persona}."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return "I apologize, but I couldn't generate a response at this time."

# Function to generate keywords based on ICH type
def generate_keywords(ich_type):
    prompt = f"Generate 3 creative keywords related to {ich_type} intangible cultural heritage art. Return only the keywords separated by commas, no explanations."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate only keywords, no explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=50
        )
        keywords = response.choices[0].message.content.split(',')
        return [k.strip() for k in keywords]
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return ["传统工艺", "文化传承", "创新设计"]

# Function to generate proposals based on keyword
def generate_proposals(keyword, ich_type):
    prompt = f"Generate 3 innovative proposal ideas for {ich_type} art products based on the keyword '{keyword}'. Each proposal should be a short phrase (under 15 words). Return only the proposals separated by commas, no explanations."
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Generate only short proposal phrases, no explanations."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100
        )
        proposals = response.choices[0].message.content.split(',')
        return [p.strip() for p in proposals]
    except Exception as e:
        st.error(f"Error calling OpenAI API: {str(e)}")
        return [f"一个{keyword}的首饰盒", f"一个{keyword}的时尚的包袋", f"一个{keyword}的首饰盒"]

# Main sidebar with title
with st.sidebar:
    st.title("🎨 ICH+ AI Generator")
    st.write("非遗文化艺术产品提案生成器")
    st.markdown("---")
    st.write("💡 输入非遗类型开始创作之旅")

# Main application header
st.markdown('<div class="app-title">🏛️ ICH+ AI Proposal Generator</div>', unsafe_allow_html=True)
st.markdown('<div class="app-subtitle">非遗文化艺术产品智能提案生成系统</div>', unsafe_allow_html=True)

# Input section
st.markdown('<div class="input-section">', unsafe_allow_html=True)
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    ich_type = st.text_input("🎭 请输入非遗类型", "", key="ich_input", placeholder="例如：大漆工艺、刺绣、陶瓷等")
    
    if st.button("🚀 开始生成", use_container_width=True):
        if ich_type:
            st.session_state['generated_keywords'] = generate_keywords(ich_type)
            st.session_state['show_personas'] = True
            st.success(f"已为 '{ich_type}' 生成关键词！")
        else:
            st.warning("请输入非遗类型")
st.markdown('</div>', unsafe_allow_html=True)

# Display personas and chat interface if keywords have been generated
if st.session_state['show_personas']:
    st.markdown('<div class="section-header">🤖 AI Agent 对话交流</div>', unsafe_allow_html=True)
    
    # Create columns for personas
    persona_cols = st.columns([1, 1, 1, 1])
    
    # Art Creator Persona
    with persona_cols[0]:
        st.markdown('<div class="persona-card">', unsafe_allow_html=True)
        st.markdown('<div class="persona-title">🎨 年轻手工艺创作者</div>', unsafe_allow_html=True)
        
        # Display chat history for art creator
        for message in st.session_state['chat_history']["art_creator"]:
            st.markdown(f'<div class="chat-message">{message}</div>', unsafe_allow_html=True)
        
        # Initial message or chat continuation
        if not st.session_state['chat_history']["art_creator"]:
            art_creator_msg = f"我想要一些{ich_type}的工艺品创意"
            st.markdown(f'<div class="chat-message">{art_creator_msg}</div>', unsafe_allow_html=True)
            st.session_state['chat_history']["art_creator"].append(art_creator_msg)
        
        # Chat for more button
        if st.button("💬 继续对话", key="chat_creator", use_container_width=True):
            creator_response = get_ai_response(f"Give me creative ideas for {ich_type} art products", "creative artisan")
            st.session_state['chat_history']["art_creator"].append(creator_response)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Art Collector Persona
    with persona_cols[1]:
        st.markdown('<div class="persona-card">', unsafe_allow_html=True)
        st.markdown('<div class="persona-title">🏺 年轻手工艺收藏者</div>', unsafe_allow_html=True)
        
        # Display chat history for art collector
        for message in st.session_state['chat_history']["art_collector"]:
            st.markdown(f'<div class="chat-message">{message}</div>', unsafe_allow_html=True)
        
        # Initial message or chat continuation
        if not st.session_state['chat_history']["art_collector"]:
            art_collector_msg = f"我想要一些拥有{ich_type}装饰的收藏品"
            st.markdown(f'<div class="chat-message">{art_collector_msg}</div>', unsafe_allow_html=True)
            st.session_state['chat_history']["art_collector"].append(art_collector_msg)
        
        # Chat for more button
        if st.button("💬 继续对话", key="chat_collector", use_container_width=True):
            collector_response = get_ai_response(f"Suggest collectible {ich_type} art pieces for a young collector", "art collector")
            st.session_state['chat_history']["art_collector"].append(collector_response)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Art Appreciator Persona
    with persona_cols[2]:
        st.markdown('<div class="persona-card">', unsafe_allow_html=True)
        st.markdown('<div class="persona-title">👁️ 年轻手工艺欣赏者</div>', unsafe_allow_html=True)
        
        # Display chat history for art appreciator
        for message in st.session_state['chat_history']["art_appreciator"]:
            st.markdown(f'<div class="chat-message">{message}</div>', unsafe_allow_html=True)
        
        # Initial message or chat continuation
        if not st.session_state['chat_history']["art_appreciator"]:
            art_appreciator_msg = f"我喜欢{ich_type}的纹理"
            st.markdown(f'<div class="chat-message">{art_appreciator_msg}</div>', unsafe_allow_html=True)
            st.session_state['chat_history']["art_appreciator"].append(art_appreciator_msg)
        
        # Chat for more button
        if st.button("💬 继续对话", key="chat_appreciator", use_container_width=True):
            appreciator_response = get_ai_response(f"Describe the aesthetic appeal of {ich_type} art", "art appreciator")
            st.session_state['chat_history']["art_appreciator"].append(appreciator_response)
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # AI Agent User
    with persona_cols[3]:
        st.markdown('<div class="persona-card" style="background-color: #e8f4f8; border-color: #4a90a4;">', unsafe_allow_html=True)
        st.markdown('<div class="persona-title" style="color: #4a90a4; border-color: #4a90a4;">👤 用户画像设置</div>', unsafe_allow_html=True)
        
        # User profile form
        with st.form(key='user_profile_form'):
            name = st.text_input("姓名", "")
            age = st.text_input("年龄", "")
            profession = st.text_input("职业", "")
            submitted = st.form_submit_button("📝 添加用户画像", use_container_width=True)
            
            if submitted and name:
                st.success(f"用户画像已添加：{name}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Display keyword section
    st.markdown('<div class="section-header">🔑 设计提案关键词生成</div>', unsafe_allow_html=True)
    
    # Create columns for keywords
    keyword_cols = st.columns(4)
    
    # Display generated keywords
    for i, keyword in enumerate(st.session_state['generated_keywords'][:3]):
        with keyword_cols[i]:
            st.markdown(f'<div class="keyword-badge">关键词 {i+1}</div>', unsafe_allow_html=True)
            st.markdown(f"<h4 style='text-align: center; color: #6a0dad;'>{keyword}</h4>", unsafe_allow_html=True)
            
            # Select keyword button
            if st.button("✅ 选择此关键词", key=f"select_keyword_{i}", use_container_width=True):
                st.session_state['selected_keyword'] = keyword
                if keyword not in st.session_state['proposals']:
                    st.session_state['proposals'][keyword] = generate_proposals(keyword, ich_type)
                st.rerun()
    
    # Add placeholder for the 4th column
    with keyword_cols[3]:
        st.markdown(f'<div class="keyword-badge">更多关键词</div>', unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #999;'>即将生成...</p>", unsafe_allow_html=True)
    
    # Display proposals if a keyword is selected
    if st.session_state['selected_keyword']:
        keyword = st.session_state['selected_keyword']
        st.markdown(f'<div class="section-header">💡 基于 "{keyword}" 的设计提案</div>', unsafe_allow_html=True)
        
        # Create columns for proposals
        proposal_cols = st.columns(4)
        
        # Display generated proposals
        for i, proposal in enumerate(st.session_state['proposals'][keyword][:3]):
            with proposal_cols[i]:
                st.markdown(f'<div class="proposal-card">', unsafe_allow_html=True)
                st.markdown(f"<h5 style='color: #6a0dad; text-align: center;'>提案 {i+1}</h5>", unsafe_allow_html=True)
                
                # Format the proposal text with highlighted keyword
                highlighted_proposal = proposal.replace(keyword, f'<span class="highlighted-text">{keyword}</span>')
                st.markdown(f'<p style="text-align: center;">"{highlighted_proposal}"</p>', unsafe_allow_html=True)
                
                # Select proposal button
                if st.button("🎯 生成设计方案", key=f"generate_proposal_{i}", use_container_width=True):
                    st.session_state['selected_proposal'] = proposal
                    st.rerun()
                
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Add placeholder for the 4th column
        with proposal_cols[3]:
            st.markdown(f'<div class="proposal-card">', unsafe_allow_html=True)
            st.markdown("<h5 style='color: #6a0dad; text-align: center;'>更多提案</h5>", unsafe_allow_html=True)
            st.markdown("<p style='text-align: center; color: #999;'>正在构思中...</p>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Display innovative design section if a proposal is selected
    if st.session_state['selected_proposal']:
        st.markdown('<div class="section-header">🚀 创新设计方案</div>', unsafe_allow_html=True)
        
        # Create columns for the innovative design
        design_cols = st.columns([1, 3])
        
        with design_cols[0]:
            # Display the selected proposal
            proposal = st.session_state['selected_proposal']
            highlighted_proposal = proposal.replace(st.session_state['selected_keyword'], 
                                                   f'<span class="highlighted-text">{st.session_state["selected_keyword"]}</span>')
            st.markdown(f'<div class="proposal-card">', unsafe_allow_html=True)
            st.markdown(f"<h4 style='color: #6a0dad; text-align: center;'>选中的提案</h4>", unsafe_allow_html=True)
            st.markdown(f'<p style="text-align: center; font-size: 1.1em;">"{highlighted_proposal}"</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Select and join button
            if st.button("🎉 确认并实施方案", use_container_width=True):
                st.success("🎊 提案已确认，准备开始实施！")
        
        with design_cols[1]:
            # Create a simple mind map for the design
            st.markdown("""
            <div style="display: flex; justify-content: center; margin-top: 20px;">
                <div style="position: relative; width: 600px; height: 300px; background-color: white; border-radius: 15px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); padding: 20px;">
                    <!-- Central node -->
                    <div style="position: absolute; left: 250px; top: 120px; background-color: #d4b3ff; border-radius: 20px; padding: 15px; text-align: center; width: 120px; font-weight: bold; color: #6a0dad;">
                        工艺方式创新
                    </div>
                    
                    <!-- Connected nodes -->
                    <div style="position: absolute; left: 50px; top: 60px; background-color: #f0e6ff; border-radius: 20px; padding: 10px; text-align: center; width: 120px; border: 2px solid #d4b3ff;">
                        视觉内容创新
                    </div>
                    
                    <div style="position: absolute; left: 450px; top: 60px; background-color: #f0e6ff; border-radius: 20px; padding: 10px; text-align: center; width: 120px; border: 2px solid #d4b3ff;">
                        透明树脂 · 大漆
                    </div>
                    
                    <div style="position: absolute; left: 450px; top: 120px; background-color: #f0e6ff; border-radius: 20px; padding: 10px; text-align: center; width: 120px; border: 2px solid #d4b3ff;">
                        可降解材料+大漆
                    </div>
                    
                    <div style="position: absolute; left: 450px; top: 180px; background-color: #f0e6ff; border-radius: 20px; padding: 10px; text-align: center; width: 120px; border: 2px solid #d4b3ff;">
                        3D打印 · 大漆
                    </div>
                    
                    <div style="position: absolute; left: 50px; top: 180px; background-color: #f0e6ff; border-radius: 20px; padding: 10px; text-align: center; width: 120px; border: 2px solid #d4b3ff;">
                        载体形态创新
                    </div>
                    
                    <!-- Connection lines -->
                    <svg style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: -1;">
                        <line x1="170" y1="80" x2="250" y2="140" style="stroke:#6a0dad;stroke-width:3" />
                        <line x1="170" y1="200" x2="250" y2="140" style="stroke:#6a0dad;stroke-width:3" />
                        <line x1="370" y1="140" x2="450" y2="80" style="stroke:#6a0dad;stroke-width:3" />
                        <line x1="370" y1="140" x2="450" y2="140" style="stroke:#6a0dad;stroke-width:3" />
                        <line x1="370" y1="140" x2="450" y2="200" style="stroke:#6a0dad;stroke-width:3" />
                    </svg>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # More details button
            st.markdown('<div style="text-align: right; margin-top: 20px;"><button style="background-color: #6a0dad; color: white; border-radius: 20px; padding: 10px 20px; border: none; cursor: pointer;">📋 查看详细方案</button></div>', unsafe_allow_html=True)

if __name__ == "__main__":
    # This will run the Streamlit app
    pass
