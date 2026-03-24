import streamlit as st
import pandas as pd
from main import process_claims
import io

st.set_page_config(
    page_title="Warranty Fraud Detector | Uttam Tiwari",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    
    .main-container {
        background: white;
        border-radius: 20px;
        padding: 40px;
        margin: 20px;
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .hero-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 50px 40px;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 40px;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.4);
        position: relative;
        overflow: hidden;
    }
    
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        right: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 0.8; }
    }
    
    .hero-title {
        font-size: 3.5rem;
        font-weight: 700;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .hero-subtitle {
        font-size: 1.3rem;
        margin-top: 15px;
        opacity: 0.95;
        font-weight: 300;
        position: relative;
        z-index: 1;
    }
    
    .creator-info {
        margin-top: 25px;
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 30px;
        position: relative;
        z-index: 1;
    }
    
    .creator-badge {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
        padding: 12px 25px;
        border-radius: 50px;
        border: 2px solid rgba(255,255,255,0.3);
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .creator-badge:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    
    .social-link {
        color: white;
        text-decoration: none;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .social-link:hover {
        transform: scale(1.05);
    }
    
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: #1a202c;
        margin: 30px 0 20px 0;
        padding-bottom: 10px;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    .upload-box {
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
        border: 2px dashed #667eea;
        border-radius: 15px;
        padding: 30px;
        text-align: center;
        margin: 20px 0;
        transition: all 0.3s ease;
    }
    
    .upload-box:hover {
        border-color: #764ba2;
        box-shadow: 0 5px 20px rgba(102, 126, 234, 0.15);
    }
    
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 15px 40px;
        font-weight: 600;
        font-size: 1.1rem;
        border-radius: 50px;
        box-shadow: 0 8px 20px rgba(102, 126, 234, 0.3);
        transition: all 0.3s ease;
        width: 100%;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 12px 30px rgba(102, 126, 234, 0.4);
    }
    
    .kpi-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .kpi-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        border-left: 5px solid;
    }
    
    .kpi-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }
    
    .kpi-total {
        border-left-color: #667eea;
        background: linear-gradient(135deg, #f6f8fb 0%, #ffffff 100%);
    }
    
    .kpi-approve {
        border-left-color: #10b981;
        background: linear-gradient(135deg, #ecfdf5 0%, #ffffff 100%);
    }
    
    .kpi-reject {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #fef2f2 0%, #ffffff 100%);
    }
    
    .kpi-escalate {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #fffbeb 0%, #ffffff 100%);
    }
    
    .kpi-number {
        font-size: 3rem;
        font-weight: 700;
        margin: 10px 0;
    }
    
    .kpi-label {
        font-size: 0.9rem;
        color: #64748b;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .info-box {
        background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%);
        border-left: 4px solid #3b82f6;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: #1e40af;
    }
    
    .success-box {
        background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
        border-left: 4px solid #10b981;
        padding: 20px;
        border-radius: 10px;
        margin: 20px 0;
        color: #065f46;
    }
    
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    }
    
    .trace-expander {
        background: #f8fafc;
        border-radius: 10px;
        margin: 10px 0;
        border: 1px solid #e2e8f0;
    }
    
    .footer {
        text-align: center;
        padding: 40px 20px;
        color: white;
        margin-top: 60px;
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
    }
    
    .feature-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .feature-card {
        background: white;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.12);
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 15px;
    }
    
    .feature-title {
        font-size: 1.2rem;
        font-weight: 600;
        margin-bottom: 10px;
        color: #1a202c;
    }
    
    .feature-desc {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero-header">
        <h1 class="hero-title">🛡️ Warranty Fraud Detector</h1>
        <p class="hero-subtitle">AI-Powered Multi-Agent System for Intelligent Warranty Claim Analysis</p>
        <div class="creator-info">
            <div class="creator-badge">
                Built by <strong>Uttam Tiwari</strong>
            </div>
            <a href="https://github.com/Uttamxalpha" target="_blank" class="social-link">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                GitHub
            </a>
            <a href="https://www.linkedin.com/in/uttam-tiwari-097025273/" target="_blank" class="social-link">
                <svg width="24" height="24" fill="currentColor" viewBox="0 0 24 24"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg>
                LinkedIn
            </a>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-container">', unsafe_allow_html=True)

st.markdown(
    """
    <div class="feature-grid">
        <div class="feature-card">
            <div class="feature-icon">📋</div>
            <div class="feature-title">Policy Validation</div>
            <div class="feature-desc">Automated verification against warranty terms and conditions</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">🔍</div>
            <div class="feature-title">Fraud Detection</div>
            <div class="feature-desc">AI-powered risk scoring using advanced ML algorithms</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <div class="feature-title">Evidence Analysis</div>
            <div class="feature-desc">Comprehensive claim investigation and documentation</div>
        </div>
        <div class="feature-card">
            <div class="feature-icon">⚖️</div>
            <div class="feature-title">Smart Decisions</div>
            <div class="feature-desc">Intelligent approval, rejection, or escalation recommendations</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("")

col1, col2 = st.columns([3, 1])

with col1:
    st.markdown('<h2 class="section-header">📤 Upload Claims Data</h2>', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Drop your CSV file here",
        type=["csv"],
        help="Upload a CSV file containing warranty claims data"
    )
    st.markdown(
        '<div class="info-box"><strong>📝 Expected Format:</strong> Each row represents one warranty claim. The system will add: policy_check, fraud_score, evidence, and decision columns.</div>',
        unsafe_allow_html=True
    )

with col2:
    st.markdown('<h2 class="section-header">🚀 Actions</h2>', unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    generate_button = st.button("🔬 Analyze Claims", key="generate", use_container_width=True)

results_df = None
uploaded_df = None

if 'results_df' in st.session_state:
    results_df = st.session_state['results_df']

if uploaded_file is not None:
    try:
        uploaded_df = pd.read_csv(uploaded_file)
    except Exception as e:
        st.error(f"❌ Could not read CSV: {e}")

    if uploaded_df is not None:
        st.markdown('<h3 class="section-header">👀 Data Preview</h3>', unsafe_allow_html=True)
        st.dataframe(uploaded_df.head(10), use_container_width=True)

        if generate_button:
            placeholder = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()

            def progress_cb(current, total):
                pct = int(current / total * 100)
                progress_bar.progress(pct)
                status_text.info(f"🔄 Processing claim {current} of {total}...")

            with st.spinner("🤖 AI Agents are analyzing claims..."):
                results_df = process_claims(uploaded_df, progress_callback=progress_cb)

            st.session_state['results_df'] = results_df

            progress_bar.progress(100)
            status_text.success("✅ Analysis complete!")

        else:
            st.markdown(
                '<div class="info-box">👆 Click <strong>"Analyze Claims"</strong> to start processing with AI agents</div>',
                unsafe_allow_html=True
            )

else:
    st.markdown(
        '<div class="info-box">📁 Please upload a CSV file to begin fraud detection analysis</div>',
        unsafe_allow_html=True
    )

if results_df is not None:
    st.markdown('<h2 class="section-header">📊 Analysis Results</h2>', unsafe_allow_html=True)
    
    if not results_df.empty:
        total = len(results_df)
        approves = int((results_df['decision'] == 'Approve claim').sum())
        rejects = int((results_df['decision'] == 'Reject claim').sum())
        escalates = int((results_df['decision'] == 'Escalate to HITL').sum())

        st.markdown(
            f"""
            <div class="kpi-container">
                <div class="kpi-card kpi-total">
                    <div class="kpi-label">Total Claims</div>
                    <div class="kpi-number">{total}</div>
                </div>
                <div class="kpi-card kpi-approve">
                    <div class="kpi-label">✅ Approved</div>
                    <div class="kpi-number" style="color: #10b981">{approves}</div>
                </div>
                <div class="kpi-card kpi-reject">
                    <div class="kpi-label">❌ Rejected</div>
                    <div class="kpi-number" style="color: #ef4444">{rejects}</div>
                </div>
                <div class="kpi-card kpi-escalate">
                    <div class="kpi-label">⚠️ Escalated</div>
                    <div class="kpi-number" style="color: #f59e0b">{escalates}</div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 5px">Manual Review Required</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown('<h3 class="section-header">📋 Detailed Results Table</h3>', unsafe_allow_html=True)

    def style_decision(val):
        if val == 'Approve claim':
            return 'background-color: #d1fae5; color: #065f46; font-weight: 600'
        if val == 'Reject claim':
            return 'background-color: #fee2e2; color: #991b1b; font-weight: 600'
        if val == 'Escalate to HITL':
            return 'background-color: #fef3c7; color: #92400e; font-weight: 600'
        return ''

    styled = results_df.style.applymap(style_decision, subset=['decision'])
    st.dataframe(styled, use_container_width=True)

    csv_bytes = results_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "📥 Download Results as CSV",
        data=csv_bytes,
        file_name="processed_claims.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.markdown("---")
    st.markdown('<h3 class="section-header">🤖 AI Agent Trace Viewer</h3>', unsafe_allow_html=True)
    
    st.markdown(
        '<div class="info-box">🔍 Select a claim below to view the complete AI agent conversation and decision-making process</div>',
        unsafe_allow_html=True
    )
    
    sel_idx = st.selectbox(
        "Choose a claim to inspect:",
        options=list(range(len(results_df))),
        format_func=lambda i: f"Claim #{i+1} - {results_df.iloc[i].get('claim_id', 'N/A')} - Decision: {results_df.iloc[i]['decision']}",
    )

    trace = results_df.iloc[sel_idx].get('agent_trace', [])

    if not trace:
        st.info("ℹ️ No agent trace available for this claim.")
    else:
        for idx, step in enumerate(trace, 1):
            agent = step.get('agent', 'Unknown Agent')
            prompt = step.get('prompt', '')
            response = step.get('response', '')
            
            agent_icons = {
                'policy_check_agent': '📋',
                'fraud_scoring_agent': '🔍',
                'evidence_collector_agent': '📊',
                'action_agent': '⚖️'
            }
            
            icon = agent_icons.get(agent, '🤖')
            
            with st.expander(f"{icon} Step {idx}: {agent.replace('_', ' ').title()}", expanded=idx==1):
                st.markdown("**📤 Agent Prompt:**")
                st.code(prompt, language='text')
                st.markdown("**📥 Agent Response:**")
                st.code(response, language='text')

st.markdown('</div>', unsafe_allow_html=True)

st.markdown(
    """
    <div class="footer">
        <p style="font-size: 1.1rem; margin-bottom: 10px">
            <strong>Built with ❤️ by Uttam Tiwari</strong>
        </p>
        <p style="opacity: 0.9">
            Powered by LangGraph • Multi-Agent AI • Groq LLM
        </p>
        <p style="margin-top: 15px; opacity: 0.8; font-size: 0.9rem">
            © 2025 Warranty Fraud Detection System. All rights reserved.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)