import React, { useState, useEffect } from 'react';
import { Clock, AlertTriangle, CheckCircle2, ShieldAlert } from 'lucide-react';

const parseUTCDate = (dateStr) => {
  if (!dateStr) return new Date();
  if (dateStr instanceof Date) return dateStr;
  let str = String(dateStr).trim();
  // If no timezone offset (+/- or Z) is present, append 'Z' to treat as UTC time
  if (!str.endsWith('Z') && !str.includes('+') && !str.includes('Z')) {
    str += 'Z';
  }
  return new Date(str);
};

export default function SLACountdown({ deadlineAt, status, resolvedAt, createdAt, escalationLevel }) {
  const [timeLeft, setTimeLeft] = useState({ hours: 0, minutes: 0, seconds: 0, isOverdue: false, totalSeconds: 0 });

  useEffect(() => {
    if (status === 'Resolved') return;

    const calculateTime = () => {
      const target = parseUTCDate(deadlineAt).getTime();
      const now = new Date().getTime();
      const diff = target - now;

      if (diff <= 0) {
        setTimeLeft({ hours: 0, minutes: 0, seconds: 0, isOverdue: true, totalSeconds: 0 });
      } else {
        const totalSeconds = Math.floor(diff / 1000);
        const hours = Math.floor(totalSeconds / 3600);
        const minutes = Math.floor((totalSeconds % 3600) / 60);
        const seconds = totalSeconds % 60;
        setTimeLeft({ hours, minutes, seconds, isOverdue: false, totalSeconds });
      }
    };

    calculateTime();
    const interval = setInterval(calculateTime, 1000);
    return () => clearInterval(interval);
  }, [deadlineAt, status]);

  if (status === 'Resolved') {
    let durationText = '';
    if (resolvedAt && createdAt) {
      const hrs = Math.max(0.1, (parseUTCDate(resolvedAt) - parseUTCDate(createdAt)) / 3600000).toFixed(1);
      durationText = `in ${hrs} hrs`;
    }
    return (
      <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-emerald-500/20 text-emerald-600 dark:text-emerald-400 border border-emerald-500/30 text-xs font-bold">
        <CheckCircle2 className="w-3.5 h-3.5" />
        <span>Resolved ✓ {durationText}</span>
      </div>
    );
  }

  if (timeLeft.isOverdue || status === 'OVERDUE' || status === 'ESCALATED') {
    return (
      <div className="space-y-1">
        <div className="inline-flex items-center space-x-1.5 px-3 py-1 rounded-full bg-red-500/20 text-red-600 dark:text-red-400 border border-red-500/40 text-xs font-extrabold animate-pulse">
          <AlertTriangle className="w-3.5 h-3.5" />
          <span>00:00:00 OVERDUE</span>
        </div>
        {escalationLevel && escalationLevel !== 'Level 1: Local Authority' && (
          <p className="text-[10px] font-bold text-red-600 dark:text-red-400 flex items-center gap-1">
            <ShieldAlert className="w-3 h-3 text-red-500" />
            <span>⚠ SLA Breached • Escalated to: {escalationLevel.replace('Level ', 'L')}</span>
          </p>
        )}
      </div>
    );
  }

  const pad = (n) => String(n).padStart(2, '0');
  const timerStr = `${pad(timeLeft.hours)}:${pad(timeLeft.minutes)}:${pad(timeLeft.seconds)}`;
  const isWarning = timeLeft.totalSeconds < 12 * 3600; // < 12 hours remaining

  return (
    <div className={`inline-flex items-center space-x-1.5 px-3 py-1 rounded-full text-xs font-bold border transition-colors ${
      isWarning 
        ? 'bg-amber-500/20 text-amber-700 dark:text-amber-300 border-amber-500/40 animate-pulse' 
        : 'bg-indigo-500/20 text-indigo-700 dark:text-indigo-300 border-indigo-500/30'
    }`}>
      <Clock className={`w-3.5 h-3.5 ${isWarning ? 'text-amber-600 dark:text-amber-400' : 'text-indigo-600 dark:text-indigo-400'}`} />
      <span className="font-mono tracking-wider">{timerStr} remaining</span>
    </div>
  );
}
