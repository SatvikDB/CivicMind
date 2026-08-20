const API_BASE = '/api';

export async function loginUser(email, password, role = null) {
  try {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, role }),
    });
    if (!res.ok) {
      const err = await res.json();
      throw new Error(err.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error("Login failed:", err);
    throw err;
  }
}

export async function fetchDemoUsers() {
  try {
    const res = await fetch(`${API_BASE}/auth/demo-users`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch demo users:", err);
    return [];
  }
}

export async function fetchComplaints(params = {}) {
  try {
    const url = new URL(`${window.location.origin}${API_BASE}/complaints`);
    Object.keys(params).forEach(key => {
      if (params[key] && params[key] !== 'All') {
        url.searchParams.append(key, params[key]);
      }
    });
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch complaints:", err);
    throw err;
  }
}

export async function fetchComplaintById(id) {
  try {
    const res = await fetch(`${API_BASE}/complaints/${id}`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to fetch complaint ${id}:`, err);
    throw err;
  }
}

export async function submitComplaint(data) {
  try {
    const res = await fetch(`${API_BASE}/complaints`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    if (!res.ok) {
      const errorData = await res.json();
      throw new Error(errorData.detail || `HTTP ${res.status}`);
    }
    return await res.json();
  } catch (err) {
    console.error("Failed to submit complaint:", err);
    throw err;
  }
}

export async function updateComplaintStatus(id, status) {
  try {
    const res = await fetch(`${API_BASE}/complaints/${id}/status`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ status }),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to update status for complaint ${id}:`, err);
    throw err;
  }
}

export async function resolveComplaint(id, payload) {
  try {
    const res = await fetch(`${API_BASE}/complaints/${id}/resolve`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error(`Failed to resolve complaint ${id}:`, err);
    throw err;
  }
}

export async function fetchDashboardStats() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/stats`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch dashboard stats:", err);
    throw err;
  }
}

export async function fetchDashboardAnalytics() {
  try {
    const res = await fetch(`${API_BASE}/dashboard/analytics`);
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch dashboard analytics:", err);
    throw err;
  }
}

export async function fetchMapComplaints(params = {}) {
  try {
    const url = new URL(`${window.location.origin}${API_BASE}/map/complaints`);
    Object.keys(params).forEach(key => {
      if (params[key] && params[key] !== 'All') {
        url.searchParams.append(key, params[key]);
      }
    });
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    return await res.json();
  } catch (err) {
    console.error("Failed to fetch map complaints:", err);
    throw err;
  }
}
