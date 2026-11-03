import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  Server, Laptop, Cpu, Shield, Plus, Search,
  HardDrive, Calendar, User, Wrench, Key, Network
} from 'lucide-react';

const STATUS_COLORS = {
  ACTIVE: 'bg-emerald-950/80 text-emerald-300 border-emerald-500/40',
  IN_STOCK: 'bg-sky-950/80 text-sky-300 border-sky-500/40',
  UNDER_MAINTENANCE: 'bg-amber-950/80 text-amber-300 border-amber-500/40',
  RETIRED: 'bg-slate-800 text-slate-400 border-slate-700',
  LOST: 'bg-rose-950/80 text-rose-300 border-rose-500/40',
};

export const AssetsPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [activeTab, setActiveTab] = useState('hardware'); // 'hardware' | 'licenses' | 'topology'
  const [assets, setAssets] = useState([]);
  const [licenses, setLicenses] = useState([]);
  const [topology, setTopology] = useState({ nodes: [], edges: [] });
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [typeFilter, setTypeFilter] = useState('');
  const [statusFilter, setStatusFilter] = useState('');

  // Modals
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [createForm, setCreateForm] = useState({
    asset_tag: '',
    serial_number: '',
    manufacturer: '',
    model: '',
    asset_type: 'LAPTOP',
    location: 'Building A - Floor 4',
    specifications: '',
    status: 'ACTIVE'
  });

  const fetchData = async () => {
    setLoading(true);
    try {
      const [astRes, licRes, topRes] = await Promise.all([
        api.get('/assets'),
        api.get('/assets/licenses/list'),
        api.get('/assets/cmdb/topology')
      ]);
      setAssets(astRes.data);
      setLicenses(licRes.data);
      setTopology(topRes.data);
    } catch (e) {
      console.error(e);
      addToast('Failed to load asset & CMDB inventory', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleCreateSubmit = async (e) => {
    e.preventDefault();
    try {
      await api.post('/assets', createForm);
      addToast(`Asset ${createForm.asset_tag} registered!`, 'success');
      setShowCreateModal(false);
      setCreateForm({
        asset_tag: '',
        serial_number: '',
        manufacturer: '',
        model: '',
        asset_type: 'LAPTOP',
        location: 'Building A - Floor 4',
        specifications: '',
        status: 'ACTIVE'
      });
      fetchData();
    } catch (err) {
      addToast(err.response?.data?.detail || 'Failed to register asset', 'error');
    }
  };

  const filteredAssets = assets.filter((a) => {
    if (typeFilter && a.asset_type !== typeFilter) return false;
    if (statusFilter && a.status !== statusFilter) return false;
    if (search) {
      const s = search.toLowerCase();
      return (
        a.asset_tag.toLowerCase().includes(s) ||
        a.model.toLowerCase().includes(s) ||
        a.manufacturer.toLowerCase().includes(s) ||
        a.serial_number.toLowerCase().includes(s)
      );
    }
    return true;
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Configuration Management Database (CMDB)</h1>
          <p className="text-xs text-slate-400 mt-0.5">Asset lifecycle, hardware tracking, software licenses & service topologies</p>
        </div>

        <div className="flex items-center space-x-3">
          <div className="flex rounded-lg bg-slate-900 border border-slate-800 p-1 text-xs font-semibold">
            <button
              onClick={() => setActiveTab('hardware')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'hardware' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Hardware CI ({assets.length})
            </button>
            <button
              onClick={() => setActiveTab('licenses')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'licenses' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Licenses ({licenses.length})
            </button>
            <button
              onClick={() => setActiveTab('topology')}
              className={`px-3 py-1 rounded-md transition-colors ${
                activeTab === 'topology' ? 'bg-brand-600 text-white shadow' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              CMDB Topology
            </button>
          </div>

          <button
            onClick={() => setShowCreateModal(true)}
            className="flex items-center space-x-1.5 px-3.5 py-2 rounded-lg bg-brand-600 hover:bg-brand-500 font-semibold text-xs text-white shadow-lg shadow-brand-500/25 transition-all"
          >
            <Plus className="w-4 h-4" />
            <span>Register Asset</span>
          </button>
        </div>
      </div>

      {/* Tab 1: Hardware CI List */}
      {activeTab === 'hardware' && (
        <div className="space-y-4">
          {/* Filters */}
          <div className="p-4 rounded-xl bg-slate-900/80 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
            <div className="relative w-full md:w-96">
              <Search className="w-4 h-4 text-slate-500 absolute left-3 top-2.5" />
              <input
                type="text"
                placeholder="Search by asset tag, serial, manufacturer, model..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                className="w-full bg-slate-950 border border-slate-700/80 rounded-lg pl-9 pr-3 py-1.5 text-xs text-slate-200 placeholder-slate-500 focus:outline-none focus:border-brand-500"
              />
            </div>

            <div className="flex items-center space-x-2 w-full md:w-auto">
              <select
                value={typeFilter}
                onChange={(e) => setTypeFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300"
              >
                <option value="">All Asset Types</option>
                <option value="LAPTOP">Laptop</option>
                <option value="SERVER">Server</option>
                <option value="SWITCH">Switch</option>
                <option value="ROUTER">Router</option>
                <option value="PRINTER">Printer</option>
              </select>

              <select
                value={statusFilter}
                onChange={(e) => setStatusFilter(e.target.value)}
                className="bg-slate-950 border border-slate-700 rounded-lg px-2.5 py-1.5 text-xs text-slate-300"
              >
                <option value="">All Statuses</option>
                <option value="ACTIVE">Active</option>
                <option value="IN_STOCK">In Stock</option>
                <option value="UNDER_MAINTENANCE">Under Maintenance</option>
                <option value="RETIRED">Retired</option>
              </select>
            </div>
          </div>

          {/* Asset Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {filteredAssets.map((ast) => (
              <div
                key={ast.id}
                className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-3 text-xs hover:border-slate-700 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <span className="font-mono font-bold text-brand-400">{ast.asset_tag}</span>
                    <span className="text-slate-500">•</span>
                    <span className="text-slate-400 text-[11px]">{ast.asset_type}</span>
                  </div>
                  <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${STATUS_COLORS[ast.status]}`}>
                    {ast.status}
                  </span>
                </div>

                <div>
                  <h3 className="font-bold text-slate-100 text-sm">{ast.manufacturer} {ast.model}</h3>
                  <div className="text-[11px] text-slate-500 font-mono mt-0.5">S/N: {ast.serial_number}</div>
                </div>

                <div className="p-3 rounded-xl bg-slate-950 border border-slate-800/80 space-y-1.5 text-[11px]">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Assigned To:</span>
                    <span className="font-semibold text-slate-200">{ast.assigned_user_name || 'In Warehouse Pool'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Location:</span>
                    <span className="text-slate-300">{ast.location}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Warranty:</span>
                    <span className="text-amber-400 font-medium">
                      {ast.warranty_expiration ? new Date(ast.warranty_expiration).toLocaleDateString() : 'N/A'}
                    </span>
                  </div>
                </div>

                {ast.specifications && (
                  <div className="text-[11px] text-slate-400 line-clamp-2 italic">
                    {ast.specifications}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Tab 2: Software Licenses */}
      {activeTab === 'licenses' && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/60 overflow-hidden shadow-xl">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-900 border-b border-slate-800 text-slate-400 font-semibold uppercase text-[10px] tracking-wider">
              <tr>
                <th className="py-3 px-4">Software Name</th>
                <th className="py-3 px-4">Publisher</th>
                <th className="py-3 px-4">License Key Mask</th>
                <th className="py-3 px-4">Seat Utilization</th>
                <th className="py-3 px-4">Expiration Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {licenses.map((lic) => {
                const pct = Math.round((lic.allocated_seats / lic.total_seats) * 100);
                return (
                  <tr key={lic.id} className="hover:bg-slate-800/40">
                    <td className="py-3.5 px-4 font-bold text-slate-100">{lic.name}</td>
                    <td className="py-3.5 px-4 text-slate-400">{lic.publisher}</td>
                    <td className="py-3.5 px-4 font-mono text-slate-400">••••-••••-{lic.license_key.slice(-4)}</td>
                    <td className="py-3.5 px-4">
                      <div className="flex items-center space-x-2">
                        <div className="w-24 bg-slate-800 h-2 rounded-full overflow-hidden">
                          <div
                            className={`h-full rounded-full ${pct > 90 ? 'bg-rose-500' : 'bg-brand-500'}`}
                            style={{ width: `${pct}%` }}
                          ></div>
                        </div>
                        <span className="text-slate-300 font-semibold">{lic.allocated_seats}/{lic.total_seats} ({pct}%)</span>
                      </div>
                    </td>
                    <td className="py-3.5 px-4 text-slate-400">
                      {lic.expiration_date ? new Date(lic.expiration_date).toLocaleDateString() : 'Perpetual'}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Tab 3: Topology Graph Visualizer */}
      {activeTab === 'topology' && (
        <div className="p-6 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-sm font-bold text-white flex items-center space-x-2">
                <Network className="w-4 h-4 text-brand-400" />
                <span>Configuration Item (CI) Dependency Topology</span>
              </h2>
              <p className="text-xs text-slate-400">Relationship map across enterprise servers, databases, and network switches</p>
            </div>
            <span className="px-2.5 py-1 rounded bg-slate-800 text-brand-300 font-mono text-xs border border-slate-700">
              {topology.nodes.length} CIs • {topology.edges.length} Relationships
            </span>
          </div>

          <div className="p-8 rounded-xl bg-slate-950 border border-slate-800 min-h-[360px] flex flex-col justify-center items-center">
            <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 w-full max-w-3xl">
              <div className="p-4 rounded-xl bg-slate-900 border border-brand-500/40 text-center space-y-1">
                <div className="text-[10px] uppercase font-bold text-brand-400">Layer 1: Perimeter Edge</div>
                <div className="font-bold text-slate-100 text-sm">Palo Alto 5220 HA</div>
                <div className="text-[11px] text-slate-500 font-mono">10.0.0.1</div>
                <div className="text-[10px] text-emerald-400 font-semibold">● ACTIVE</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-cyan-500/40 text-center space-y-1">
                <div className="text-[10px] uppercase font-bold text-cyan-400">Layer 2: Core Routing</div>
                <div className="font-bold text-slate-100 text-sm">Cisco Catalyst 9300</div>
                <div className="text-[11px] text-slate-500 font-mono">10.0.0.2</div>
                <div className="text-[10px] text-emerald-400 font-semibold">● ACTIVE</div>
              </div>

              <div className="p-4 rounded-xl bg-slate-900 border border-purple-500/40 text-center space-y-1">
                <div className="text-[10px] uppercase font-bold text-purple-400">Layer 3: Application Clusters</div>
                <div className="font-bold text-slate-100 text-sm">HPE ProLiant DL380</div>
                <div className="text-[11px] text-slate-500 font-mono">10.0.2.15</div>
                <div className="text-[10px] text-emerald-400 font-semibold">● ACTIVE</div>
              </div>
            </div>

            <div className="mt-8 text-center text-xs text-slate-500">
              Bi-directional CMDB relationships mapped: <code className="text-brand-300">Edge Firewall → DEPENDS_ON → Core Switch → HOSTS → Database Cluster</code>
            </div>
          </div>
        </div>
      )}

      {/* Register Asset Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 z-50 bg-black/75 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl w-full max-w-lg shadow-2xl p-6">
            <h2 className="text-base font-bold text-white mb-4 flex items-center space-x-2">
              <Server className="w-4 h-4 text-brand-400" />
              <span>Register New Configuration Item / Asset</span>
            </h2>

            <form onSubmit={handleCreateSubmit} className="space-y-4 text-xs">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Asset Tag</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. AST-MAC-0199"
                    value={createForm.asset_tag}
                    onChange={(e) => setCreateForm({ ...createForm, asset_tag: e.target.value.toUpperCase() })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 font-mono"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Serial Number</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. C02G78949AA"
                    value={createForm.serial_number}
                    onChange={(e) => setCreateForm({ ...createForm, serial_number: e.target.value.toUpperCase() })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100 font-mono"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Manufacturer</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Apple / Dell / Cisco"
                    value={createForm.manufacturer}
                    onChange={(e) => setCreateForm({ ...createForm, manufacturer: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                  />
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Model</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. MacBook Pro 16 M3 Max"
                    value={createForm.model}
                    onChange={(e) => setCreateForm({ ...createForm, model: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Asset Type</label>
                  <select
                    value={createForm.asset_type}
                    onChange={(e) => setCreateForm({ ...createForm, asset_type: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-200"
                  >
                    <option value="LAPTOP">Laptop</option>
                    <option value="DESKTOP">Desktop</option>
                    <option value="SERVER">Server</option>
                    <option value="SWITCH">Switch</option>
                    <option value="ROUTER">Router</option>
                    <option value="PRINTER">Printer</option>
                    <option value="MOBILE">Mobile</option>
                  </select>
                </div>

                <div>
                  <label className="block font-semibold text-slate-300 mb-1">Physical Location</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Building A - Floor 4"
                    value={createForm.location}
                    onChange={(e) => setCreateForm({ ...createForm, location: e.target.value })}
                    className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2.5 text-slate-100"
                  />
                </div>
              </div>

              <div>
                <label className="block font-semibold text-slate-300 mb-1">Hardware Specifications</label>
                <textarea
                  rows={2}
                  placeholder="e.g. 64GB RAM, 2TB SSD, 16-Core CPU..."
                  value={createForm.specifications}
                  onChange={(e) => setCreateForm({ ...createForm, specifications: e.target.value })}
                  className="w-full bg-slate-950 border border-slate-700 rounded-lg p-2 text-slate-100"
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
                  Save Asset
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
