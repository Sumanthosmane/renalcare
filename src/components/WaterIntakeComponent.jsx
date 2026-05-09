import React, { useState, useEffect } from 'react';
import { Droplet, Plus, Minus, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { logWaterIntake, getDailyWaterSummary } from '../api';

export default function WaterIntakeComponent({ patientId = 'patient_demo_001' }) {
  const [amount, setAmount] = useState(250);
  const [time, setTime] = useState('12:00');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState(null);
  const [dailySummary, setDailySummary] = useState(null);
  const [showHistory, setShowHistory] = useState(false);

  // Daily goal is 2-3 liters (2500ml recommended for kidney stone prevention)
  const DAILY_GOAL = 2500;

  // Fetch daily summary on mount
  useEffect(() => {
    fetchDailySummary();
    const interval = setInterval(fetchDailySummary, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, [patientId]);

  const fetchDailySummary = async () => {
    try {
      const summary = await getDailyWaterSummary(patientId);
      setDailySummary(summary);
    } catch (err) {
      console.error('Failed to fetch water summary:', err);
    }
  };

  const handleAddWater = async () => {
    if (amount <= 0) {
      setError('Please enter a valid amount (greater than 0)');
      return;
    }

    setLoading(true);
    setError(null);
    setSuccess(false);

    try {
      console.log('Logging water intake:', { patientId, amount, time, notes });
      const result = await logWaterIntake(patientId, amount, time, notes);
      console.log('Water intake logged:', result);
      
      setSuccess(true);
      setAmount(250);
      setNotes('');
      setTime(new Date().toTimeString().slice(0, 5));
      
      // Refresh summary
      await fetchDailySummary();
      
      // Hide success message after 3 seconds
      setTimeout(() => setSuccess(false), 3000);
    } catch (err) {
      console.error('Water intake error:', err);
      setError(err.message || 'Failed to log water intake. Make sure backend is running on port 8001');
    } finally {
      setLoading(false);
    }
  };

  const quickAmounts = [250, 500, 750, 1000];
  const currentIntake = dailySummary?.total_intake_ml || 0;
  const percentage = Math.min((currentIntake / DAILY_GOAL) * 100, 100);
  const remaining = Math.max(DAILY_GOAL - currentIntake, 0);

  return (
    <div className="w-full max-w-2xl mx-auto p-6 bg-white rounded-2xl shadow-lg border border-slate-200" id="hydration">
      <div className="flex items-center gap-3 mb-6">
        <Droplet className="w-6 h-6 text-cyan-600" />
        <h2 className="text-2xl font-bold text-slate-800">Hydration Tracker</h2>
      </div>

      {/* Daily Progress */}
      <div className="mb-8 p-6 bg-gradient-to-r from-cyan-50 to-blue-50 rounded-xl border border-cyan-200">
        <div className="flex items-center justify-between mb-4">
          <div>
            <p className="text-sm text-slate-600 font-medium">Today's Hydration</p>
            <p className="text-3xl font-bold text-blue-600 mt-1">
              {currentIntake} <span className="text-lg text-slate-600">ml</span>
            </p>
            <p className="text-sm text-slate-500 mt-2">
              Goal: {DAILY_GOAL}ml | Remaining: {remaining}ml
            </p>
          </div>
          <div className="text-right">
            <div className="text-4xl font-bold text-cyan-600">{Math.round(percentage)}%</div>
            <p className="text-sm text-slate-600 mt-1">of daily goal</p>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full bg-slate-200 rounded-full h-3 overflow-hidden">
          <div
            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 transition-all duration-500 rounded-full"
            style={{ width: `${percentage}%` }}
          />
        </div>

        {/* Status Message */}
        <div className="mt-4 flex items-center gap-2">
          {percentage >= 100 ? (
            <>
              <CheckCircle className="w-5 h-5 text-green-600" />
              <p className="text-sm font-semibold text-green-700">
                ✓ Daily goal achieved! Great job staying hydrated!
              </p>
            </>
          ) : percentage >= 75 ? (
            <>
              <Droplet className="w-5 h-5 text-blue-600" />
              <p className="text-sm font-semibold text-blue-700">
                Almost there! {remaining}ml more to reach your goal.
              </p>
            </>
          ) : (
            <>
              <AlertCircle className="w-5 h-5 text-yellow-600" />
              <p className="text-sm font-semibold text-yellow-700">
                Keep drinking! {remaining}ml remaining.
              </p>
            </>
          )}
        </div>
      </div>

      {/* Quick Add Buttons */}
      <div className="mb-8">
        <p className="text-sm font-semibold text-slate-700 mb-3">Quick Add</p>
        <div className="grid grid-cols-4 gap-3">
          {quickAmounts.map((amt) => (
            <button
              key={amt}
              onClick={() => setAmount(amt)}
              className={`py-3 px-2 rounded-lg font-bold transition-all ${
                amount === amt
                  ? 'bg-blue-600 text-white shadow-lg'
                  : 'bg-slate-100 text-slate-700 hover:bg-slate-200'
              }`}
            >
              {amt} <span className="text-xs block mt-1">ml</span>
            </button>
          ))}
        </div>
      </div>

      {/* Custom Input */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        {/* Amount */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Amount (ml)
          </label>
          <div className="flex items-center gap-2 bg-slate-100 rounded-lg p-2">
            <button
              onClick={() => setAmount(Math.max(50, amount - 50))}
              className="p-2 hover:bg-slate-200 rounded-lg transition-colors"
            >
              <Minus className="w-5 h-5 text-slate-600" />
            </button>
            <input
              type="number"
              value={amount}
              onChange={(e) => setAmount(Math.max(0, parseInt(e.target.value) || 0))}
              className="flex-1 bg-transparent text-center font-bold text-lg outline-none"
              min="0"
            />
            <button
              onClick={() => setAmount(amount + 50)}
              className="p-2 hover:bg-slate-200 rounded-lg transition-colors"
            >
              <Plus className="w-5 h-5 text-slate-600" />
            </button>
          </div>
        </div>

        {/* Time */}
        <div>
          <label className="block text-sm font-semibold text-slate-700 mb-2">
            Time
          </label>
          <input
            type="time"
            value={time}
            onChange={(e) => setTime(e.target.value)}
            className="w-full px-4 py-2 border border-slate-300 rounded-lg font-medium text-slate-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
      </div>

      {/* Notes */}
      <div className="mb-6">
        <label className="block text-sm font-semibold text-slate-700 mb-2">
          Notes (Optional)
        </label>
        <input
          type="text"
          value={notes}
          onChange={(e) => setNotes(e.target.value)}
          placeholder="e.g., With meal, after exercise"
          className="w-full px-4 py-2 border border-slate-300 rounded-lg text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}

      {/* Success */}
      {success && (
        <div className="mb-4 p-4 bg-green-50 border border-green-200 rounded-lg flex items-start gap-3">
          <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 flex-shrink-0" />
          <p className="text-sm text-green-700">Water intake logged successfully! 💧</p>
        </div>
      )}

      {/* Log Button */}
      <button
        onClick={handleAddWater}
        disabled={loading}
        className={`w-full py-3 px-4 rounded-lg font-semibold transition-all flex items-center justify-center gap-2 mb-6 ${
          loading
            ? 'bg-slate-400 text-white cursor-not-allowed'
            : 'bg-gradient-to-r from-cyan-600 to-blue-600 text-white hover:from-cyan-700 hover:to-blue-700 cursor-pointer'
        }`}
      >
        {loading ? (
          <>
            <Loader className="w-5 h-5 animate-spin" />
            Logging...
          </>
        ) : (
          <>
            <Droplet className="w-5 h-5" />
            Log Water Intake
          </>
        )}
      </button>

      {/* Today's Log */}
      {dailySummary?.intakes && dailySummary.intakes.length > 0 && (
        <div className="border-t border-slate-200 pt-6">
          <button
            onClick={() => setShowHistory(!showHistory)}
            className="text-sm font-semibold text-blue-600 hover:text-blue-700 mb-3"
          >
            {showHistory ? '▼ Hide' : '▶ Show'} Today's Log ({dailySummary.intakes.length})
          </button>

          {showHistory && (
            <div className="space-y-2 max-h-48 overflow-y-auto">
              {dailySummary.intakes.map((intake, idx) => (
                <div
                  key={idx}
                  className="p-3 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between"
                >
                  <div>
                    <p className="text-sm font-semibold text-slate-800">
                      {intake.amount_ml} ml
                    </p>
                    <p className="text-xs text-slate-500">
                      {intake.time} {intake.notes ? `• ${intake.notes}` : ''}
                    </p>
                  </div>
                  <Droplet className="w-4 h-4 text-cyan-600" />
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Hydration Tips */}
      <div className="mt-8 p-4 bg-blue-50 rounded-lg border border-blue-200">
        <p className="text-sm font-semibold text-blue-900 mb-2">💡 Hydration Tips</p>
        <ul className="text-xs text-blue-800 space-y-1 list-disc list-inside">
          <li>Drink water consistently throughout the day</li>
          <li>2.5-3 liters daily helps prevent kidney stones</li>
          <li>More water if you exercise or live in hot climate</li>
          <li>Monitor your urine color (pale = well hydrated)</li>
        </ul>
      </div>
    </div>
  );
}
