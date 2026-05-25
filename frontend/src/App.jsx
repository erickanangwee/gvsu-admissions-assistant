import { useState, useRef, useEffect } from 'react';
import { v4 as uuidv4 } from 'uuid';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';

const SESSION_ID  = uuidv4();
const API_BASE    = 'http://localhost:8000/api/v1';
const TOPIC_CHIPS = ['Freshman', 'Transfer', 'Graduate', 'Financial Aid', 'Housing'];

// GVSU brand colors
const GVSU_NAVY  = '#1B4F8A';
const GVSU_GOLD  = '#FFC72C';
const GVSU_LIGHT = '#E8F0F9';

function SourceCard({ title, url }) {
  return (
    <a
      href={url}
      target="_blank"
      rel="noreferrer"
      style={{
        display: 'block',
        marginTop: '6px',
        padding: '6px 10px',
        background: GVSU_LIGHT,
        border: `1px solid #B5D4F4`,
        borderRadius: '8px',
        fontSize: '12px',
        color: GVSU_NAVY,
        textDecoration: 'none',
        overflow: 'hidden',
        textOverflow: 'ellipsis',
        whiteSpace: 'nowrap',
      }}
    >
      🔗 {title}
    </a>
  );
}

function Message({ msg }) {
  const isUser = msg.role === 'user';
  return (
    <div style={{
      display: 'flex',
      justifyContent: isUser ? 'flex-end' : 'flex-start',
      marginBottom: '16px',
    }}>
      {!isUser && (
        <div style={{
          width: '30px', height: '30px', borderRadius: '50%',
          background: GVSU_NAVY, color: '#fff',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: '12px', fontWeight: '600', marginRight: '8px',
          flexShrink: 0, marginTop: '2px',
        }}>G</div>
      )}
      <div style={{
        maxWidth: '78%',
        background: isUser ? GVSU_NAVY : '#fff',
        color: isUser ? '#fff' : '#1a1a1a',
        borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
        padding: '10px 14px',
        border: isUser ? 'none' : '1px solid #D8E6F5',
        fontSize: '14px',
        lineHeight: '1.55',
      }}>
        {isUser
          ? <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>{msg.content}</p>
          : <div className="md-body"><ReactMarkdown remarkPlugins={[remarkGfm]}>{msg.content}</ReactMarkdown></div>
        }

        {!isUser && msg.pages_fetched > 0 && (
          <div style={{
            display: 'inline-block',
            marginTop: '8px',
            fontSize: '11px',
            background: GVSU_LIGHT,
            color: GVSU_NAVY,
            padding: '2px 8px',
            borderRadius: '20px',
            border: '1px solid #B5D4F4',
          }}>
            {msg.pages_fetched} gvsu.edu {msg.pages_fetched === 1 ? 'page' : 'pages'} searched
          </div>
        )}

        {msg.sources?.length > 0 && (
          <div style={{ marginTop: '8px', borderTop: '1px solid #E8EFF8', paddingTop: '8px' }}>
            <p style={{ fontSize: '11px', color: '#6B8BB5', margin: '0 0 4px 0' }}>Sources</p>
            {msg.sources.map((s, i) => <SourceCard key={i} {...s} />)}
          </div>
        )}
      </div>
    </div>
  );
}

function SearchingIndicator() {
  return (
    <div style={{ display: 'flex', alignItems: 'flex-start', marginBottom: '16px' }}>
      <div style={{
        width: '30px', height: '30px', borderRadius: '50%',
        background: GVSU_NAVY, color: '#fff',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontSize: '12px', fontWeight: '600', marginRight: '8px', flexShrink: 0,
      }}>G</div>
      <div style={{
        background: '#fff', border: '1px solid #D8E6F5',
        borderRadius: '18px 18px 18px 4px',
        padding: '10px 16px', fontSize: '13px', color: '#6B8BB5',
        display: 'flex', alignItems: 'center', gap: '8px',
      }}>
        <span style={{
          display: 'inline-block',
          width: '14px', height: '14px',
          border: `2px solid ${GVSU_GOLD}`,
          borderTopColor: GVSU_NAVY,
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
        }} />
        Searching gvsu.edu…
      </div>
    </div>
  );
}

export default function App() {
  const [messages,  setMessages]  = useState([{
    role: 'assistant',
    content: 'Hi! I can answer questions about GVSU admissions, deadlines, financial aid, housing, and more. I search gvsu.edu live to give you the most up-to-date answers.',
    sources: [],
    pages_fetched: 0,
  }]);
  const [input,   setInput]   = useState('');
  const [loading, setLoading] = useState(false);
  const [topic,   setTopic]   = useState(null);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  async function sendMessage() {
    if (!input.trim() || loading) return;
    const userMsg = input.trim();
    setInput('');

    const newMessages = [
      ...messages,
      { role: 'user', content: userMsg, sources: [], pages_fetched: 0 }
    ];
    setMessages(newMessages);
    setLoading(true);

    try {
      const res = await fetch(`${API_BASE}/chat`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          session_id: SESSION_ID,
          message:    userMsg,
          topic:      topic,
          history:    newMessages.slice(-10).map(m => ({
            role: m.role, content: m.content,
          })),
        }),
      });

      const data = await res.json();
      setMessages(prev => [...prev, {
        role:         'assistant',
        content:      data.answer,
        sources:      data.sources || [],
        pages_fetched: data.pages_fetched || 0,
      }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'Something went wrong. Please try again.',
        sources: [],
        pages_fetched: 0,
      }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100vh', background: '#F4F7FB' }}>
      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        * { box-sizing: border-box; }
        body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }
        input:focus { outline: none; box-shadow: 0 0 0 2px #1B4F8A44; }
        ::-webkit-scrollbar { width: 5px; }
        ::-webkit-scrollbar-thumb { background: #CBD5E1; border-radius: 4px; }
        .md-body { font-size: 14px; line-height: 1.6; color: #1a1a1a; }
        .md-body p { margin: 0 0 8px 0; }
        .md-body p:last-child { margin-bottom: 0; }
        .md-body h1, .md-body h2, .md-body h3 { color: #1B4F8A; margin: 12px 0 6px 0; font-size: 14px; font-weight: 700; }
        .md-body h1 { font-size: 15px; }
        .md-body ul, .md-body ol { margin: 4px 0 8px 0; padding-left: 20px; }
        .md-body li { margin-bottom: 3px; }
        .md-body strong { color: #1a1a1a; font-weight: 600; }
        .md-body hr { border: none; border-top: 1px solid #E2EAF4; margin: 10px 0; }
        .md-body table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 13px; }
        .md-body th { background: #E8F0F9; color: #1B4F8A; padding: 6px 10px; text-align: left; border: 1px solid #B5D4F4; }
        .md-body td { padding: 5px 10px; border: 1px solid #D8E6F5; }
        .md-body tr:nth-child(even) td { background: #F4F7FB; }
        .md-body blockquote { border-left: 3px solid #FFC72C; margin: 8px 0; padding: 4px 12px; background: #FFFBF0; color: #5a4a00; border-radius: 0 6px 6px 0; }
      `}</style>

      {/* Header */}
      <header style={{
        background: GVSU_NAVY, color: '#fff', padding: '0 24px',
        display: 'flex', alignItems: 'center', gap: '12px',
        height: '60px', flexShrink: 0,
        borderBottom: `3px solid ${GVSU_GOLD}`,
      }}>
        <div style={{
          width: '36px', height: '36px', borderRadius: '8px',
          background: GVSU_GOLD, display: 'flex', alignItems: 'center',
          justifyContent: 'center', fontWeight: '800', fontSize: '18px', color: GVSU_NAVY,
        }}>G</div>
        <div style={{ flex: 1 }}>
          <div style={{ fontWeight: '600', fontSize: '15px', letterSpacing: '0.01em' }}>
            GVSU Admissions Assistant
          </div>
          <div style={{ fontSize: '11px', color: 'rgba(255,255,255,0.65)', marginTop: '1px' }}>
            Searches gvsu.edu live · Powered by Claude AI
          </div>
        </div>
        <button
          onClick={() => setMessages([messages[0]])}
          style={{
            background: 'transparent', border: '1px solid rgba(255,255,255,0.3)',
            color: 'rgba(255,255,255,0.7)', borderRadius: '6px',
            padding: '5px 12px', fontSize: '12px', cursor: 'pointer',
          }}
        >
          Clear chat
        </button>
      </header>

      {/* Topic chips */}
      <div style={{
        display: 'flex', gap: '8px', flexWrap: 'wrap',
        padding: '10px 24px', background: '#fff',
        borderBottom: '1px solid #E2EAF4',
      }}>
        {TOPIC_CHIPS.map(t => (
          <button
            key={t}
            onClick={() => setTopic(topic === t ? null : t)}
            style={{
              padding: '4px 14px', borderRadius: '20px', fontSize: '12px',
              fontWeight: '500', cursor: 'pointer', transition: 'all 0.15s',
              background: topic === t ? GVSU_NAVY : '#fff',
              color: topic === t ? '#fff' : GVSU_NAVY,
              border: `1.5px solid ${topic === t ? GVSU_NAVY : '#B5D4F4'}`,
            }}
          >{t}</button>
        ))}
        {topic && (
          <button
            onClick={() => setTopic(null)}
            style={{
              padding: '4px 10px', borderRadius: '20px', fontSize: '12px',
              cursor: 'pointer', background: '#FFF4D6',
              color: '#8B6000', border: '1.5px solid #FFC72C',
            }}
          >
            ✕ {topic}
          </button>
        )}
      </div>

      {/* Messages */}
      <main style={{ flex: 1, overflowY: 'auto', padding: '20px 24px' }}>
        <div style={{ maxWidth: '720px', margin: '0 auto' }}>
          {messages.map((m, i) => <Message key={i} msg={m} />)}
          {loading && <SearchingIndicator />}
          <div ref={bottomRef} />
        </div>
      </main>

      {/* Input */}
      <footer style={{
        background: '#fff', borderTop: '1px solid #E2EAF4',
        padding: '12px 24px',
      }}>
        <div style={{
          maxWidth: '720px', margin: '0 auto',
          display: 'flex', gap: '10px', alignItems: 'center',
        }}>
          <input
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={e => e.key === 'Enter' && !e.shiftKey && sendMessage()}
            placeholder="Ask about admissions, deadlines, financial aid, housing…"
            disabled={loading}
            style={{
              flex: 1, border: '1.5px solid #B5D4F4', borderRadius: '24px',
              padding: '10px 18px', fontSize: '14px', background: '#F4F7FB',
              color: '#1a1a1a', transition: 'border 0.15s',
            }}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            style={{
              background: loading || !input.trim() ? '#B5D4F4' : GVSU_NAVY,
              color: '#fff', border: 'none', borderRadius: '24px',
              padding: '10px 22px', fontSize: '14px', fontWeight: '500',
              cursor: loading || !input.trim() ? 'not-allowed' : 'pointer',
              transition: 'background 0.15s', whiteSpace: 'nowrap',
            }}
          >
            {loading ? 'Searching…' : 'Send'}
          </button>
        </div>
        <p style={{
          textAlign: 'center', fontSize: '11px', color: '#94A3B8',
          marginTop: '8px', maxWidth: '720px', margin: '8px auto 0',
        }}>
          Answers are sourced live from gvsu.edu. For official decisions, always confirm with GVSU Admissions.
        </p>
      </footer>
    </div>
  );
}