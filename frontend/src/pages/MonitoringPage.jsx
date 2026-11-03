import React, { useState, useEffect } from 'react';
import api from '../api/axios';
import { useAuth } from '../context/AuthContext';
import { useNotification } from '../context/NotificationContext';
import {
  Activity, Server, Database, Radio, RefreshCw,
  AlertTriangle, ShieldAlert, Cpu, HardDrive, Wifi, Zap
} from 'lucide-react';

export const MonitoringPage = () => {
  const { user, primaryRole } = useAuth();
  const { addToast } = useNotification();

  const [devices, setDevices] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pulsing, setPulsing] = useState(false);

  const fetchData = async () => {
    try {
      const [devRes, alertRes] = await Promise.all([
        api.get('/monitoring/devices'),
        api.get('/monitoring/alerts?status=ACTIVE')
      ]);
      setDevices(devRes.data);
      setAlerts(alertRes.data);
    } catch (e) {
      console.error(e);
      addToast('Failed to load telemetry', 'error');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handlePulse = async () => {
    setPulsing(true);
    try {
      await api.post('/monitoring/pulse');
      addToast('Simulated real-time infrastructure telemetry pulse received!', 'success');
      fetchData();
    } catch (e) {
      addToast('Telemetry pulse failed', 'error');
    } finally {
      setPulsing(false);
    }
  };

  const handleSimulatePrometheusWebhook = async () => {
    try {
      const samplePayload = {
        receiver: 'itsm-webhook-receiver',
        status: 'firing',
        alerts: [
          {
            labels: { alertname: 'HighCPUThresholdExceeded', severity: 'critical' },
            annotations: { summary: 'App-Server-Web01 CPU load exceeded 95% threshold for 5m' }
          }
        ]
      };
      await api.post('/monitoring/webhook/prometheus', samplePayload);
      addToast('Prometheus Alertmanager webhook triggered! Incident created.', 'warning');
      fetchData();
    } catch (e) {
      addToast('Webhook dispatch failed', 'error');
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-xl font-bold text-white tracking-tight">Infrastructure Monitoring & APM Telemetry</h1>
          <p className="text-xs text-slate-400 mt-0.5">Real-time health, CPU/RAM/Disk metrics, and automated alert-to-incident ingestion</p>
        </div>

        <div className="flex items-center space-x-3">
          <button
            onClick={handleSimulatePrometheusWebhook}
            className="flex items-center space-x-1.5 px-3 py-1.5 rounded-lg bg-rose-950/80 hover:bg-rose-900 border border-rose-500/50 text-rose-300 font-semibold text-xs transition-colors"
            title="Simulate incoming alert from Prometheus Alertmanager"
          >
            <Zap className="w-3.5 h-3.5 text-rose-400" />
            <span>Test Prometheus Webhook</span>
          </button>

          <button
            onClick={handlePulse}
            disabled={pulsing}
            className="flex items-center space-x-1.5 px-3.5 py-1.5 rounded-lg bg-brand-600 hover:bg-brand-500 font-semibold text-xs text-white shadow-lg shadow-brand-500/25 transition-all disabled:opacity-50"
          >
            <RefreshCw className={`w-3.5 h-3.5 ${pulsing ? 'animate-spin' : ''}`} />
            <span>Send Telemetry Pulse</span>
          </button>
        </div>
      </div>

      {/* Active Threshold Breaches Banner */}
      {alerts.length > 0 && (
        <div className="p-4 rounded-xl bg-amber-950/40 border border-amber-500/40 space-y-2">
          <div className="flex items-center space-x-2 text-xs font-bold text-amber-300">
            <AlertTriangle className="w-4 h-4 text-amber-400" />
            <span>Active Threshold Violations ({alerts.length})</span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {alerts.map((al) => (
              <div key={al.id} className="p-2.5 rounded-lg bg-slate-950/80 border border-slate-800 text-xs flex justify-between items-center">
                <div>
                  <div className="font-bold text-slate-200">{al.device_name}: {al.alert_name}</div>
                  <div className="text-[11px] text-slate-400">{al.message}</div>
                </div>
                <span className="px-2 py-0.5 rounded bg-rose-950 text-rose-300 font-bold text-[10px] border border-rose-500/40">
                  {al.severity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Live Monitored Devices Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {devices.map((dev) => {
          const cpu = dev.latest_cpu || 0;
          const mem = dev.latest_memory || 0;
          const disk = dev.latest_disk || 0;

          return (
            <div
              key={dev.id}
              className="p-5 rounded-2xl bg-slate-900/90 border border-slate-800 shadow-xl space-y-4 text-xs"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <div className="p-2 rounded-lg bg-slate-800 text-brand-400">
                    {dev.device_type === 'DATABASE' ? <Database className="w-4 h-4" /> : <Server className="w-4 h-4" />}
                  </div>
                  <div>
                    <h3 className="font-bold text-slate-100 text-sm">{dev.name}</h3>
                    <div className="text-[10px] text-slate-500 font-mono">{dev.ip_address}</div>
                  </div>
                </div>

                <div className="flex items-center space-x-1.5 px-2 py-0.5 rounded-full bg-emerald-950/80 border border-emerald-500/40 text-emerald-400 font-semibold text-[10px]">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                  <span>{dev.latest_health || 'HEALTHY'}</span>
                </div>
              </div>

              {/* Resource Utilization Gauges */}
              <div className="space-y-3 pt-2">
                {/* CPU */}
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Cpu className="w-3 h-3 text-slate-500" />
                      <span>CPU Utilization</span>
                    </span>
                    <span className={`font-mono font-bold ${cpu > 90 ? 'text-rose-400' : 'text-slate-200'}`}>
                      {cpu}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        cpu > 90 ? 'bg-rose-500' : cpu > 75 ? 'bg-amber-500' : 'bg-brand-500'
                      }`}
                      style={{ width: `${Math.min(cpu, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Memory */}
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <HardDrive className="w-3 h-3 text-slate-500" />
                      <span>Memory (RAM)</span>
                    </span>
                    <span className={`font-mono font-bold ${mem > 90 ? 'text-rose-400' : 'text-slate-200'}`}>
                      {mem}%
                    </span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className={`h-full rounded-full transition-all duration-500 ${
                        mem > 90 ? 'bg-rose-500' : mem > 80 ? 'bg-amber-500' : 'bg-cyan-500'
                      }`}
                      style={{ width: `${Math.min(mem, 100)}%` }}
                    ></div>
                  </div>
                </div>

                {/* Disk */}
                <div>
                  <div className="flex justify-between text-[11px] mb-1">
                    <span className="text-slate-400 flex items-center space-x-1">
                      <Radio className="w-3 h-3 text-slate-500" />
                      <span>Storage Disk Pool</span>
                    </span>
                    <span className="font-mono font-bold text-slate-200">{disk}%</span>
                  </div>
                  <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
                    <div
                      className="bg-purple-500 h-full rounded-full transition-all duration-500"
                      style={{ width: `${Math.min(disk, 100)}%` }}
                    ></div>
                  </div>
                </div>
              </div>

              <div className="pt-2 border-t border-slate-800/80 flex items-center justify-between text-[10px] text-slate-500 font-mono">
                <span>Heartbeat: {dev.last_heartbeat ? new Date(dev.last_heartbeat).toLocaleTimeString() : 'Active'}</span>
                <span>ICMP Ping: 1.4ms</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
