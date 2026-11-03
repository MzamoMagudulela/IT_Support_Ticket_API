import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  BookOpen, Search, ThumbsUp, ThumbsDown, Eye, Plus,
  Tag, CheckCircle, ArrowLeft, Share2
} from 'lucide-react';

export const KnowledgePage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState('');
  const [selectedArticle, setSelectedArticle] = useState(null);

  // Create Modal
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    content: '',
    category: 'Network',
    tags: 'vpn,troubleshooting,guide'
  });

  const fetchArticles = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (category) params.append('category', category);
      const res = await api.get(`/knowledge?${params.toString()}`);
      setArticles(res.data);
    } catch (e) {
      console.error(e);
      addToast('Failed to load knowledge base', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchArticles();
  }, [category]);

  const handleSearchSubmit = (e) => {
    e.preventDefault();
    fetchArticles();
  };

  const handleOpenArticle = async (art) => {
    try {
      const res = await api.get(`/knowledge/${art.id}`);
      setSelectedArticle(res.data);
    } catch (err) {
      setSelectedArticle(art);
    }
  };

  const handleFeedback = async (isHelpful) => {
    if (!selectedArticle) return;
    try {
      await api.post(`/knowledge/${selectedArticle.id}/feedback`, { is_helpful: isHelpful });
      addToast(isHelpful ? 'Marked as helpful! Thank you.' : 'Feedback recorded.', 'success');
      setSelectedArticle((prev) => ({
        ...prev,
        helpful_count: isHelpful ? prev.helpful_count + 1 : prev.helpful_count,
        not_helpful_count: !isHelpful ? prev.not_helpful_count + 1 : prev.not_helpful_count
      }));
    } catch (err) {
      addToast('Feedback already recorded', 'info');
    }
  };

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/knowledge', createForm);
      addToast('Troubleshooting guide published!', 'success');
      setShowCreateModal(false);
      setCreateForm({ title: '', content: '', category: 'Network', tags: 'vpn,troubleshooting,guide' });
      fetchArticles();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to publish article', 'error');
    }
  };

  return (
    <div className="space-y-6 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">IT Knowledge Base & Solutions Directory</h1>
          <p className="text-xs text-slate-400 mt-0.5">Verified solutions, standard operating procedures (SOP), and troubleshooting documentation</p>
        </div>

        <button
          onClick={() => setShowCreateModal(true)}
          className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 font-semibold text-xs text-white shadow-lg shadow-brand-500/25 transition-all"
        >
          <Plus className="w-4 h-4" />
          <span>Publish Solution Guide</span>
        </button>
      </div>

      {selectedArticle ? (
        /* Article Reader View */
        <div className="p-6 md:p-8 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-6">
          <button
            onClick={() => setSelectedArticle(null)}
            className="flex items-center space-x-1.5 text-xs font-semibold text-slate-400 hover:text-white transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Back to Knowledge Index</span>
          </button>

          <div className="space-y-2 pb-4 border-b border-slate-800">
            <div className="flex items-center space-x-2">
              <span className="px-2.5 py-0.5 rounded-full bg-brand-950 border border-brand-500/40 text-brand-300 font-semibold text-xs">
                {selectedArticle.category}
              </span>
              <span className="text-xs text-slate-500">•</span>
              <span className="text-xs text-slate-400">Author: {selectedArticle.author_name || 'IT Support'}</span>
              <span className="text-xs text-slate-500">•</span>
              <span className="text-xs text-slate-400 flex items-center space-x-1">
                <Eye className="w-3.5 h-3.5 text-slate-500" />
                <span>{selectedArticle.view_count} views</span>
              </span>
            </div>
            <h1 className="text-2xl font-bold text-white tracking-tight">{selectedArticle.title}</h1>
          </div>

          <div className="prose prose-invert prose-sm max-w-none text-slate-200 leading-relaxed whitespace-pre-wrap font-sans text-xs">
            {selectedArticle.content}
          </div>

          {selectedArticle.tags && (
            <div className="flex items-center space-x-2 pt-4 border-t border-slate-800">
              <Tag className="w-3.5 h-3.5 text-slate-500" />
              <div className="flex space-x-1.5">
                {selectedArticle.tags.split(',').map((tag) => (
                  <span key={tag} className="px-2 py-0.5 rounded bg-slate-800 text-slate-400 text-[10px]">
                    #{tag.trim()}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Helpfulness Feedback Bar */}
          <div className="p-4 rounded-xl bg-slate-950 border border-slate-800 flex items-center justify-between text-xs">
            <span className="text-slate-300 font-medium">Was this solution article helpful in resolving your problem?</span>
            <div className="flex items-center space-x-3">
              <button
                onClick={() => handleFeedback(true)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-emerald-950/60 border border-slate-700 hover:border-emerald-500/50 text-slate-300 hover:text-emerald-300 transition-colors"
              >
                <ThumbsUp className="w-3.5 h-3.5 text-emerald-400" />
                <span>Yes ({selectedArticle.helpful_count})</span>
              </button>
              <button
                onClick={() => handleFeedback(false)}
                className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-slate-900 hover:bg-rose-950/60 border border-slate-700 hover:border-rose-500/50 text-slate-300 hover:text-rose-300 transition-colors"
              >
                <ThumbsDown className="w-3.5 h-3.5 text-rose-400" />
                <span>No ({selectedArticle.not_helpful_count})</span>
              </button>
            </div>
          </div>
        </div>
      ) : (
        /* Index List View */
        <div className="space-y-6">
          {/* Search Banner */}
          <div className="p-6 rounded-2xl bg-gradient-to-r from-brand-950/60 via-slate-900 to-slate-900 border border-slate-800 shadow-xl space-y-4">
            <form onSubmit={handleSearchSubmit} className="relative max-w-2xl">
              <Search className="w-5 h-5 text-slate-400 absolute left-4 top-3" />
              <input
                type="text"
                placeholder="Search troubleshooting guides (e.g., VPN error 809, password reset, Docker license)..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700 rounded-xl pl-12 pr-4 py-2.5 text-xs text-slate-100 placeholder-slate-500 focus:outline-none focus:border-brand-500 shadow-inner"
              />
            </form>

            <div className="flex items-center space-x-2 text-xs">
              <span className="text-slate-400 font-semibold">Filter Category:</span>
              {['', 'Network', 'Software', 'Hardware', 'Security'].map((cat) => (
                <button
                  key={cat}
                  onClick={() => setCategory(cat)}
                  className={`px-3 py-1 rounded-lg text-xs font-semibold transition-colors ${
                    category === cat
                      ? 'bg-brand-600 text-white shadow'
                      : 'bg-slate-800 text-slate-400 hover:text-slate-200'
                  }`}
                >
                  {cat || 'All Categories'}
                </button>
              ))}
            </div>
          </div>

          {/* Article Cards Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {articles.map((art) => (
              <div
                key={art.id}
                onClick={() => handleOpenArticle(art)}
                className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 shadow-lg hover:border-slate-700 cursor-pointer transition-all space-y-3 group"
              >
                <div className="flex items-center justify-between text-xs">
                  <span className="px-2 py-0.5 rounded bg-brand-950 text-brand-300 border border-brand-500/30 text-[10px] font-bold">
                    {art.category}
                  </span>
                  <span className="text-slate-500 text-[11px] flex items-center space-x-1">
                    <Eye className="w-3 h-3" />
                    <span>{art.view_count}</span>
                  </span>
                </div>

                <h3 className="font-bold text-slate-100 text-sm group-hover:text-brand-300 transition-colors line-clamp-2">
                  {art.title}
                </h3>

                <p className="text-slate-400 text-xs line-clamp-3 leading-relaxed">
                  {art.content}
                </p>

                <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[11px] text-slate-400">
                  <span>Helpful votes: <strong className="text-emerald-400">+{art.helpful_count}</strong></span>
                  <span className="text-brand-400 font-semibold group-hover:underline">Read Guide →</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Publish Article Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-xl shadow-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
              <BookOpen className="w-4 h-4 text-brand-400" />
              <span>Publish Troubleshooting Guide / SOP</span>
            </h2>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div>
                <label className="block font-semibold text-slate-300 mb-1">Article Title</label>
                <input
                  type="text"
                  required
                  placeholder="e.g. How to Resolve GlobalProtect VPN Connection Error 809"
                  value={createForm.title}
                  onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                />
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Category</label>
                  <select
                    value={createForm.category}
                    onChange={(e) => setCreateForm({ ...createForm, category: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="Network">Network</option>
                    <option value="Software">Software</option>
                    <option value="Hardware">Hardware</option>
                    <option value="Security">Security</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Tags (comma-separated)</label>
                  <input
                    type="text"
                    placeholder="vpn, remote, error809"
                    value={createForm.tags}
                    onChange={(e) => setCreateForm({ ...createForm, tags: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Markdown Body & Troubleshooting Steps</label>
                <textarea
                  rows={8}
                  required
                  placeholder="### Overview&#10;Describe problem...&#10;&#10;### Resolution Steps&#10;1. Check port 4500&#10;2. Apply registry fix..."
                  value={createForm.content}
                  onChange={(e) => setCreateForm({ ...createForm, content: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 text-slate-100 font-mono text-xs"
                />
              </div>

              <div className="flex justify-end space-x-2 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 rounded-lg bg-slate-800 text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 text-white font-semibold"
                >
                  Publish Article
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
