# 🛠️ IMPLEMENTATION GUIDE: Features 108-111
## One-Click Templates, Social Proof, Progress Visualization, Team Workspaces

**Version:** 1.0
**Last Updated:** 2025-11-17
**Estimated Total Implementation Time:** 4-6 weeks

---

## 📋 IMPLEMENTATION OVERVIEW

### Features to Implement:
1. **Feature 108:** One-Click Job Templates
2. **Feature 109:** Social Proof & Trust Signals
3. **Feature 110:** Interactive Job Progress Visualization
4. **Feature 111:** Team Workspaces & Collaboration

### Implementation Order (Recommended):
```
Week 1-2: Feature 108 (Templates) - Foundation for great UX
Week 2-3: Feature 110 (Progress) - Core user experience
Week 3-4: Feature 109 (Social Proof) - Drive conversions
Week 4-6: Feature 111 (Teams) - Enable monetization
```

**Why this order?**
- Templates first → Users can try platform immediately
- Progress viz next → Users see their jobs working (retention)
- Social proof third → Convert more visitors (growth)
- Teams last → Monetize activated users (revenue)

---

## 🎯 FEATURE 108: ONE-CLICK JOB TEMPLATES

**Goal:** Get users from landing page to first completed job in <60 seconds

### Phase 1: Database Schema (1 day)

```sql
-- templates table
CREATE TABLE job_templates (
    id SERIAL PRIMARY KEY,
    template_id VARCHAR(50) UNIQUE NOT NULL,  -- 'monte-carlo-pi'
    name VARCHAR(100) NOT NULL,
    description TEXT NOT NULL,
    icon VARCHAR(10),  -- Emoji: '📊'
    docker_image VARCHAR(255) NOT NULL,
    command_template TEXT NOT NULL,  -- Python template with {variables}
    total_chunks INT NOT NULL,
    cpu_cores_per_chunk INT NOT NULL,
    ram_gb_per_chunk FLOAT NOT NULL,
    estimated_duration_minutes INT,
    estimated_cost_credits INT,
    example_output TEXT,
    category VARCHAR(50) NOT NULL,  -- 'demo', 'ml', 'rendering', 'data'
    difficulty VARCHAR(20) NOT NULL,  -- 'beginner', 'intermediate', 'advanced'
    is_active BOOLEAN DEFAULT TRUE,
    usage_count INT DEFAULT 0,  -- Track popularity
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Track which template was used for each job
ALTER TABLE jobs ADD COLUMN template_id VARCHAR(50);
ALTER TABLE jobs ADD COLUMN template_parameters JSON;  -- Store user inputs

-- Add index for fast template queries
CREATE INDEX idx_templates_category ON job_templates(category);
CREATE INDEX idx_templates_active ON job_templates(is_active);

-- Sample data migration
INSERT INTO job_templates (
    template_id, name, description, icon, docker_image, command_template,
    total_chunks, cpu_cores_per_chunk, ram_gb_per_chunk,
    estimated_duration_minutes, estimated_cost_credits, example_output,
    category, difficulty
) VALUES (
    'monte-carlo-pi',
    'Estimate π with Monte Carlo',
    'See distributed computing in action! This demo shows linear speedup.',
    '📊',
    'python:3.11-slim',
    'python -c ''
import random
samples = {samples_per_chunk}
inside = sum(1 for _ in range(samples) if random.random()**2 + random.random()**2 <= 1)
print(f"pi_estimate={{inside / samples * 4}}")
''',
    4,
    1,
    0.5,
    2,
    10,
    'pi_estimate=3.14159265',
    'demo',
    'beginner'
);
```

**Migration command:**
```bash
alembic revision --autogenerate -m "add job templates table"
alembic upgrade head
```

---

### Phase 2: Backend API (2 days)

**File: `src/api/templates.py`**

```python
"""
Job Templates API

Endpoints:
- GET /templates - List all templates
- GET /templates/{template_id} - Get template details
- POST /templates/{template_id}/run - Run a template
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from src.database.connection import get_db
from src.database.models import JobTemplate, Job, JobChunk, User
from src.api.auth import get_current_user
from src.utils.credits import calculate_job_cost

router = APIRouter()


# Pydantic models
class JobTemplateResponse(BaseModel):
    """Template details for API response."""
    id: int
    template_id: str
    name: str
    description: str
    icon: str
    docker_image: str
    total_chunks: int
    cpu_cores_per_chunk: int
    ram_gb_per_chunk: float
    estimated_duration_minutes: int
    estimated_cost_credits: int
    example_output: str
    category: str
    difficulty: str
    usage_count: int

    class Config:
        from_attributes = True


class TemplateParameters(BaseModel):
    """User-provided parameters for template."""
    # For monte-carlo-pi
    samples_per_chunk: Optional[int] = Field(25_000_000, description="Samples per chunk")

    # For ML training
    n_estimators: Optional[int] = Field(100, description="Number of trees")
    max_depth: Optional[int] = Field(10, description="Max tree depth")

    # For video encoding
    input_video_url: Optional[str] = None
    start_time: Optional[int] = 0
    chunk_duration: Optional[int] = 10


class RunTemplateRequest(BaseModel):
    """Request to run a template."""
    parameters: Optional[Dict[str, Any]] = {}


@router.get("/templates", response_model=List[JobTemplateResponse])
async def list_templates(
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all active job templates.

    Query params:
    - category: Filter by category (demo, ml, rendering, data)
    - difficulty: Filter by difficulty (beginner, intermediate, advanced)
    """
    query = db.query(JobTemplate).filter(JobTemplate.is_active == True)

    if category:
        query = query.filter(JobTemplate.category == category)

    if difficulty:
        query = query.filter(JobTemplate.difficulty == difficulty)

    templates = query.order_by(JobTemplate.usage_count.desc()).all()

    return templates


@router.get("/templates/{template_id}", response_model=JobTemplateResponse)
async def get_template(
    template_id: str,
    db: Session = Depends(get_db)
):
    """Get template details by ID."""
    template = db.query(JobTemplate).filter(
        JobTemplate.template_id == template_id,
        JobTemplate.is_active == True
    ).first()

    if not template:
        raise HTTPException(404, f"Template '{template_id}' not found")

    return template


@router.post("/templates/{template_id}/run")
async def run_template(
    template_id: str,
    request: RunTemplateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Run a job from a template.

    This is the ONE-CLICK experience!
    """
    # 1. Find template
    template = db.query(JobTemplate).filter(
        JobTemplate.template_id == template_id,
        JobTemplate.is_active == True
    ).first()

    if not template:
        raise HTTPException(404, f"Template '{template_id}' not found")

    # 2. Check user credits
    if current_user.credit_balance < template.estimated_cost_credits:
        raise HTTPException(
            400,
            {
                "error": "insufficient_credits",
                "message": f"Need {template.estimated_cost_credits} credits, you have {current_user.credit_balance}",
                "required_credits": template.estimated_cost_credits,
                "current_balance": current_user.credit_balance,
                "shortfall": template.estimated_cost_credits - current_user.credit_balance
            }
        )

    # 3. Create job
    job = Job(
        owner_id=current_user.id,
        docker_image=template.docker_image,
        total_chunks=template.total_chunks,
        cpu_cores_per_chunk=template.cpu_cores_per_chunk,
        ram_gb_per_chunk=template.ram_gb_per_chunk,
        status="pending",
        template_id=template_id,
        template_parameters=request.parameters  # Store for reproducibility
    )

    db.add(job)
    db.flush()  # Get job.id

    # 4. Create chunks with filled-in commands
    for chunk_num in range(template.total_chunks):
        # Fill template variables
        command = template.command_template.format(
            chunk_num=chunk_num,
            **request.parameters
        )

        chunk = JobChunk(
            job_id=job.id,
            chunk_number=chunk_num,
            status="pending"
        )
        db.add(chunk)

    # 5. Deduct credits
    actual_cost = calculate_job_cost(job)
    current_user.credit_balance -= actual_cost

    # 6. Track template usage
    template.usage_count += 1

    db.commit()

    # 7. Return success with helpful info
    return {
        "success": True,
        "message": f"🚀 Started {template.name}!",
        "job_id": job.id,
        "estimated_completion": (
            datetime.now() + timedelta(minutes=template.estimated_duration_minutes)
        ).isoformat(),
        "track_url": f"/jobs/{job.id}",
        "credits_charged": actual_cost,
        "credits_remaining": current_user.credit_balance,

        # Help user understand what's happening
        "what_happens_next": [
            f"Your job is split into {template.total_chunks} chunks",
            "Chunks are assigned to available nodes",
            f"Results ready in ~{template.estimated_duration_minutes} minutes",
            "You'll see real-time progress below"
        ]
    }
```

**Register router in `src/api/main.py`:**
```python
from src.api import templates

app.include_router(templates.router, prefix="/api/v1", tags=["Templates"])
```

---

### Phase 3: Frontend Components (3 days)

**File: `frontend/src/components/TemplateGallery.tsx`**

```typescript
import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Play, Clock, Coins } from 'lucide-react';

interface Template {
  id: number;
  template_id: string;
  name: string;
  description: string;
  icon: string;
  category: string;
  difficulty: string;
  estimated_duration_minutes: number;
  estimated_cost_credits: number;
  usage_count: number;
}

export const TemplateGallery: React.FC = () => {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [runningTemplateId, setRunningTemplateId] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, [selectedCategory]);

  const fetchTemplates = async () => {
    const params = new URLSearchParams();
    if (selectedCategory) params.append('category', selectedCategory);

    const response = await fetch(`/api/v1/templates?${params}`);
    const data = await response.json();
    setTemplates(data);
    setLoading(false);
  };

  const runTemplate = async (templateId: string) => {
    setRunningTemplateId(templateId);

    try {
      const response = await fetch(`/api/v1/templates/${templateId}/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('api_key') || ''
        },
        body: JSON.stringify({ parameters: {} })
      });

      if (!response.ok) {
        const error = await response.json();
        if (error.error === 'insufficient_credits') {
          alert(`Not enough credits! Need ${error.required_credits}, you have ${error.current_balance}`);
          return;
        }
        throw new Error('Failed to run template');
      }

      const result = await response.json();

      // Show success message
      alert(result.message);

      // Redirect to job detail page
      window.location.href = `/jobs/${result.job_id}`;

    } catch (error) {
      console.error('Error running template:', error);
      alert('Failed to start job. Please try again.');
    } finally {
      setRunningTemplateId(null);
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty) {
      case 'beginner': return 'bg-green-100 text-green-800';
      case 'intermediate': return 'bg-yellow-100 text-yellow-800';
      case 'advanced': return 'bg-red-100 text-red-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">🚀 Get Started with Templates</h1>
        <p className="text-gray-600 mt-2">
          One-click demos to see distributed computing in action
        </p>
      </div>

      {/* Category filters */}
      <div className="flex gap-2">
        <Button
          variant={selectedCategory === null ? 'default' : 'outline'}
          onClick={() => setSelectedCategory(null)}
        >
          All Templates
        </Button>
        <Button
          variant={selectedCategory === 'demo' ? 'default' : 'outline'}
          onClick={() => setSelectedCategory('demo')}
        >
          📊 Demos
        </Button>
        <Button
          variant={selectedCategory === 'ml' ? 'default' : 'outline'}
          onClick={() => setSelectedCategory('ml')}
        >
          🤖 Machine Learning
        </Button>
        <Button
          variant={selectedCategory === 'rendering' ? 'default' : 'outline'}
          onClick={() => setSelectedCategory('rendering')}
        >
          🎨 Rendering
        </Button>
        <Button
          variant={selectedCategory === 'data' ? 'default' : 'outline'}
          onClick={() => setSelectedCategory('data')}
        >
          📈 Data Processing
        </Button>
      </div>

      {/* Template grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {templates.map((template) => (
          <Card key={template.id} className="hover:shadow-lg transition-shadow">
            <CardHeader>
              <div className="flex items-start justify-between">
                <span className="text-4xl">{template.icon}</span>
                <Badge className={getDifficultyColor(template.difficulty)}>
                  {template.difficulty}
                </Badge>
              </div>
              <CardTitle className="mt-4">{template.name}</CardTitle>
              <CardDescription>{template.description}</CardDescription>
            </CardHeader>

            <CardContent>
              <div className="space-y-3">
                {/* Stats */}
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <div className="flex items-center gap-1">
                    <Clock className="w-4 h-4" />
                    {template.estimated_duration_minutes} min
                  </div>
                  <div className="flex items-center gap-1">
                    <Coins className="w-4 h-4" />
                    {template.estimated_cost_credits} credits
                  </div>
                </div>

                {/* Usage count */}
                <div className="text-xs text-gray-500">
                  ✨ Run by {template.usage_count.toLocaleString()} users
                </div>

                {/* Run button */}
                <Button
                  className="w-full"
                  onClick={() => runTemplate(template.template_id)}
                  disabled={runningTemplateId === template.template_id}
                >
                  {runningTemplateId === template.template_id ? (
                    <>
                      <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                      Starting...
                    </>
                  ) : (
                    <>
                      <Play className="w-4 h-4 mr-2" />
                      Run This Demo
                    </>
                  )}
                </Button>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
};
```

---

### Phase 4: Testing (1 day)

**File: `tests/test_api/test_templates.py`**

```python
import pytest
from fastapi.testclient import TestClient


def test_list_templates(client: TestClient, db_session):
    """Test listing all templates."""
    response = client.get("/api/v1/templates")

    assert response.status_code == 200
    templates = response.json()
    assert len(templates) > 0
    assert templates[0]["template_id"] == "monte-carlo-pi"


def test_filter_templates_by_category(client: TestClient, db_session):
    """Test filtering templates by category."""
    response = client.get("/api/v1/templates?category=demo")

    assert response.status_code == 200
    templates = response.json()
    assert all(t["category"] == "demo" for t in templates)


def test_run_template_success(client: TestClient, test_user, db_session):
    """Test successfully running a template."""
    # Give user enough credits
    test_user.credit_balance = 1000
    db_session.commit()

    response = client.post(
        "/api/v1/templates/monte-carlo-pi/run",
        headers={"X-API-Key": test_user.api_key},
        json={"parameters": {"samples_per_chunk": 10_000_000}}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert "job_id" in data
    assert "estimated_completion" in data
    assert data["credits_charged"] == 10


def test_run_template_insufficient_credits(client: TestClient, test_user, db_session):
    """Test running template with insufficient credits."""
    # Give user 0 credits
    test_user.credit_balance = 0
    db_session.commit()

    response = client.post(
        "/api/v1/templates/monte-carlo-pi/run",
        headers={"X-API-Key": test_user.api_key},
        json={"parameters": {}}
    )

    assert response.status_code == 400
    data = response.json()
    assert data["error"] == "insufficient_credits"
    assert "shortfall" in data


def test_template_usage_count_increments(client: TestClient, test_user, db_session):
    """Test that template usage count increments."""
    template = db_session.query(JobTemplate).filter(
        JobTemplate.template_id == "monte-carlo-pi"
    ).first()

    initial_count = template.usage_count

    # Run template
    test_user.credit_balance = 1000
    db_session.commit()

    client.post(
        "/api/v1/templates/monte-carlo-pi/run",
        headers={"X-API-Key": test_user.api_key},
        json={"parameters": {}}
    )

    db_session.refresh(template)
    assert template.usage_count == initial_count + 1
```

---

## 📊 FEATURE 110: INTERACTIVE JOB PROGRESS VISUALIZATION

**Goal:** Users see beautiful, real-time progress instead of staring at blank screen

### Phase 1: Database Schema (0.5 days)

```sql
-- Add columns to track chunk execution details
ALTER TABLE job_chunks ADD COLUMN started_at TIMESTAMP;
ALTER TABLE job_chunks ADD COLUMN execution_time_seconds FLOAT;
ALTER TABLE job_chunks ADD COLUMN output_preview TEXT;  -- First 200 chars of output

-- Add index for fast job progress queries
CREATE INDEX idx_job_chunks_job_status ON job_chunks(job_id, status);
```

---

### Phase 2: WebSocket Backend (2 days)

**File: `src/api/websocket_progress.py`**

```python
"""
Real-time job progress via WebSocket.

Provides live updates every 2 seconds:
- Overall job progress
- Chunk status details
- Estimated time remaining
- Real-time output preview
"""

from fastapi import WebSocket, WebSocketDisconnect, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import asyncio
import json

from src.database.connection import get_db
from src.database.models import Job, JobChunk, Node


class JobProgressManager:
    """Manage WebSocket connections for job progress."""

    def __init__(self):
        # Store active connections: {job_id: [websocket1, websocket2, ...]}
        self.connections: dict[int, list[WebSocket]] = {}

    async def connect(self, job_id: int, websocket: WebSocket):
        """Register new WebSocket connection."""
        await websocket.accept()

        if job_id not in self.connections:
            self.connections[job_id] = []

        self.connections[job_id].append(websocket)

    def disconnect(self, job_id: int, websocket: WebSocket):
        """Remove WebSocket connection."""
        if job_id in self.connections:
            self.connections[job_id].remove(websocket)

            if not self.connections[job_id]:
                del self.connections[job_id]

    async def broadcast_update(self, job_id: int, data: dict):
        """Send update to all connections watching this job."""
        if job_id not in self.connections:
            return

        # Send to all connections
        dead_connections = []
        for websocket in self.connections[job_id]:
            try:
                await websocket.send_json(data)
            except:
                dead_connections.append(websocket)

        # Clean up dead connections
        for ws in dead_connections:
            self.disconnect(job_id, ws)


progress_manager = JobProgressManager()


@router.websocket("/ws/jobs/{job_id}/progress")
async def job_progress_websocket(
    websocket: WebSocket,
    job_id: int,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time job progress.

    Sends updates every 2 seconds until job completes.
    """
    await progress_manager.connect(job_id, websocket)

    try:
        while True:
            # Get latest job status
            job = db.query(Job).filter(Job.id == job_id).first()

            if not job:
                await websocket.send_json({
                    "error": "Job not found",
                    "job_id": job_id
                })
                break

            # Get chunk details
            chunks = db.query(JobChunk).filter(
                JobChunk.job_id == job_id
            ).order_by(JobChunk.chunk_number).all()

            # Build chunk status array
            chunk_statuses = []
            for chunk in chunks:
                node_name = None
                if chunk.assigned_node_id:
                    node = db.query(Node).filter(Node.id == chunk.assigned_node_id).first()
                    node_name = node.name if node else "Unknown"

                chunk_statuses.append({
                    "chunk_number": chunk.chunk_number,
                    "status": chunk.status,
                    "node_name": node_name,
                    "execution_time_seconds": chunk.execution_time_seconds,
                    "output_preview": chunk.output_preview,
                    "retry_count": chunk.retry_count
                })

            # Calculate progress
            completed_chunks = sum(1 for c in chunk_statuses if c["status"] == "completed")
            running_chunks = sum(1 for c in chunk_statuses if c["status"] == "running")
            failed_chunks = sum(1 for c in chunk_statuses if c["status"] == "failed")

            progress_percent = (completed_chunks / job.total_chunks * 100) if job.total_chunks > 0 else 0

            # Estimate time remaining
            estimated_seconds_remaining = None
            if completed_chunks > 0:
                # Average time per completed chunk
                completed_chunk_times = [
                    c["execution_time_seconds"]
                    for c in chunk_statuses
                    if c["execution_time_seconds"] is not None
                ]

                if completed_chunk_times:
                    avg_chunk_time = sum(completed_chunk_times) / len(completed_chunk_times)
                    remaining_chunks = job.total_chunks - completed_chunks - running_chunks
                    estimated_seconds_remaining = remaining_chunks * avg_chunk_time

            # Build progress update
            update = {
                "job_id": job.id,
                "status": job.status,
                "progress_percent": round(progress_percent, 1),
                "chunks_completed": completed_chunks,
                "chunks_running": running_chunks,
                "chunks_failed": failed_chunks,
                "chunks_total": job.total_chunks,
                "estimated_seconds_remaining": (
                    round(estimated_seconds_remaining)
                    if estimated_seconds_remaining else None
                ),
                "chunk_details": chunk_statuses,
                "started_at": job.created_at.isoformat() if job.created_at else None,
                "completed_at": job.completed_at.isoformat() if job.completed_at else None,
                "timestamp": datetime.now().isoformat()
            }

            # Send update
            await websocket.send_json(update)

            # If job is terminal, send final update and close
            if job.status in ['completed', 'failed', 'cancelled']:
                await asyncio.sleep(1)
                await websocket.send_json({
                    **update,
                    "final": True
                })
                break

            # Wait 2 seconds before next update
            await asyncio.sleep(2)

    except WebSocketDisconnect:
        pass
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        progress_manager.disconnect(job_id, websocket)
```

---

### Phase 3: Frontend Progress Component (3 days)

**File: `frontend/src/components/JobProgress.tsx`**

```typescript
import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Progress } from '@/components/ui/progress';
import { Badge } from '@/components/ui/badge';
import { Clock, CheckCircle, XCircle, Loader2 } from 'lucide-react';

interface ChunkStatus {
  chunk_number: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  node_name: string | null;
  execution_time_seconds: number | null;
  output_preview: string | null;
  retry_count: number;
}

interface ProgressData {
  job_id: number;
  status: string;
  progress_percent: number;
  chunks_completed: number;
  chunks_running: number;
  chunks_failed: number;
  chunks_total: number;
  estimated_seconds_remaining: number | null;
  chunk_details: ChunkStatus[];
  started_at: string;
  completed_at: string | null;
  final?: boolean;
}

export const JobProgress: React.FC<{ jobId: number }> = ({ jobId }) => {
  const [progress, setProgress] = useState<ProgressData | null>(null);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const ws = new WebSocket(`${protocol}//${window.location.host}/ws/jobs/${jobId}/progress`);

    ws.onopen = () => {
      setConnected(true);
    };

    ws.onmessage = (event) => {
      const data: ProgressData = JSON.parse(event.data);
      setProgress(data);

      if (data.final) {
        ws.close();
      }
    };

    ws.onerror = () => {
      setConnected(false);
    };

    ws.onclose = () => {
      setConnected(false);
    };

    return () => {
      ws.close();
    };
  }, [jobId]);

  if (!progress) {
    return (
      <Card className="p-8">
        <div className="flex items-center justify-center gap-3">
          <Loader2 className="w-6 h-6 animate-spin" />
          <span>Connecting to job...</span>
        </div>
      </Card>
    );
  }

  const formatTime = (seconds: number | null) => {
    if (!seconds) return 'calculating...';

    if (seconds < 60) return `${Math.round(seconds)}s`;
    if (seconds < 3600) return `${Math.round(seconds / 60)}m`;
    return `${Math.round(seconds / 3600)}h`;
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'completed': return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'running': return <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />;
      case 'failed': return <XCircle className="w-5 h-5 text-red-600" />;
      default: return <Clock className="w-5 h-5 text-gray-400" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'bg-green-500';
      case 'running': return 'bg-blue-500';
      case 'failed': return 'bg-red-500';
      default: return 'bg-gray-300';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold">Job #{jobId}</h2>
            <Badge variant={progress.status === 'running' ? 'default' : 'secondary'}>
              {progress.status}
            </Badge>
          </div>

          {/* Progress bar */}
          <div>
            <div className="flex justify-between text-sm mb-2">
              <span className="font-medium">
                Progress: {progress.chunks_completed}/{progress.chunks_total} chunks
              </span>
              <span className="text-gray-600">
                {progress.progress_percent.toFixed(1)}%
              </span>
            </div>
            <Progress value={progress.progress_percent} className="h-3" />
          </div>

          {/* Stats row */}
          <div className="grid grid-cols-3 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <Clock className="w-4 h-4 text-gray-500" />
              <div>
                <div className="font-medium">Time Remaining</div>
                <div className="text-gray-600">
                  ~{formatTime(progress.estimated_seconds_remaining)}
                </div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <CheckCircle className="w-4 h-4 text-green-500" />
              <div>
                <div className="font-medium">Completed</div>
                <div className="text-gray-600">{progress.chunks_completed}</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 text-blue-500" />
              <div>
                <div className="font-medium">Running</div>
                <div className="text-gray-600">{progress.chunks_running}</div>
              </div>
            </div>
          </div>
        </div>
      </Card>

      {/* Chunk grid */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">Live Chunk Status</h3>
        <div className="grid grid-cols-4 md:grid-cols-8 gap-3">
          {progress.chunk_details.map((chunk) => (
            <div
              key={chunk.chunk_number}
              className="border rounded-lg p-3 text-center space-y-2"
            >
              <div className="text-xs font-medium text-gray-600">
                Chunk {chunk.chunk_number}
              </div>

              <div className="flex justify-center">
                {getStatusIcon(chunk.status)}
              </div>

              {chunk.execution_time_seconds && (
                <div className="text-xs text-gray-500">
                  {chunk.execution_time_seconds.toFixed(1)}s
                </div>
              )}

              {chunk.node_name && (
                <div className="text-xs text-gray-500 truncate">
                  {chunk.node_name}
                </div>
              )}

              {chunk.retry_count > 0 && (
                <Badge variant="outline" className="text-xs">
                  Retry {chunk.retry_count}
                </Badge>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Real-time output */}
      <Card className="p-6">
        <h3 className="text-lg font-semibold mb-4">📈 Real-Time Output</h3>
        <div className="bg-black text-green-400 font-mono text-sm p-4 rounded-lg h-64 overflow-y-auto">
          {progress.chunk_details
            .filter(c => c.output_preview)
            .map((chunk, idx) => (
              <div key={idx} className="mb-1">
                <span className="text-blue-400">[Chunk {chunk.chunk_number}]</span>{' '}
                {chunk.output_preview}
              </div>
            ))}

          {progress.chunk_details.filter(c => c.output_preview).length === 0 && (
            <div className="text-gray-500">Waiting for output...</div>
          )}
        </div>
      </Card>

      {/* Connection status */}
      <div className="text-center text-sm text-gray-500">
        {connected ? (
          <span className="text-green-600">● Live updates active</span>
        ) : (
          <span className="text-red-600">● Disconnected</span>
        )}
      </div>
    </div>
  );
};
```

---

### Phase 4: Testing (1 day)

```python
def test_websocket_progress_connection(client: TestClient, test_job):
    """Test WebSocket connects successfully."""
    with client.websocket_connect(f"/ws/jobs/{test_job.id}/progress") as websocket:
        data = websocket.receive_json()

        assert "job_id" in data
        assert data["job_id"] == test_job.id
        assert "progress_percent" in data


def test_websocket_progress_updates(client, test_job, db_session):
    """Test WebSocket sends updates when chunks complete."""
    with client.websocket_connect(f"/ws/jobs/{test_job.id}/progress") as websocket:
        # Initial state
        data1 = websocket.receive_json()
        assert data1["chunks_completed"] == 0

        # Complete a chunk
        chunk = test_job.chunks[0]
        chunk.status = "completed"
        chunk.execution_time_seconds = 2.5
        db_session.commit()

        # Wait for update
        time.sleep(2.5)

        data2 = websocket.receive_json()
        assert data2["chunks_completed"] == 1
```

---

## 🌟 FEATURE 109: SOCIAL PROOF & TRUST SIGNALS

**Goal:** Convert 3x more visitors by showing real activity and testimonials

### Phase 1: Database Schema (0.5 days)

```sql
-- Track testimonials
CREATE TABLE testimonials (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    quote TEXT NOT NULL,
    author_name VARCHAR(100) NOT NULL,
    author_title VARCHAR(100),
    author_company VARCHAR(100),
    avatar_url TEXT,
    is_verified BOOLEAN DEFAULT FALSE,
    is_featured BOOLEAN DEFAULT FALSE,
    display_order INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add to jobs for activity feed
ALTER TABLE jobs ADD COLUMN is_public BOOLEAN DEFAULT TRUE;  -- Can hide if private

CREATE INDEX idx_jobs_public_completed ON jobs(is_public, completed_at DESC);
```

---

### Phase 2: Backend API (1 day)

**File: `src/api/social_proof.py`**

```python
"""
Social Proof API

Endpoints:
- GET /activity/live - Real-time activity feed
- GET /activity/stats - System-wide stats
- GET /testimonials - User testimonials
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from src.database.connection import get_db
from src.database.models import Job, User, Node, Testimonial

router = APIRouter()


@router.get("/activity/live")
async def get_live_activity(db: Session = Depends(get_db)):
    """
    Get real-time activity feed for landing page.

    Returns recent job completions (last 5 minutes) to show
    platform is active and working.
    """
    # Recent completions
    five_min_ago = datetime.now() - timedelta(minutes=5)

    recent_jobs = db.query(Job).filter(
        Job.is_public == True,
        Job.status == 'completed',
        Job.completed_at >= five_min_ago
    ).order_by(Job.completed_at.desc()).limit(20).all()

    activity_feed = []
    for job in recent_jobs:
        user = db.query(User).filter(User.id == job.owner_id).first()
        if not user:
            continue

        # Anonymize username: "Alice" → "A***"
        anonymous_name = user.username[0] + "***" if user.username else "User"

        # Calculate duration
        duration_seconds = (job.completed_at - job.created_at).total_seconds()
        duration_minutes = int(duration_seconds / 60)

        # Get template name if used
        job_type = job.template_id or "custom job"

        activity_feed.append({
            "user": anonymous_name,
            "action": f"completed {job_type}",
            "duration_minutes": duration_minutes,
            "chunks": job.total_chunks,
            "timestamp": job.completed_at.isoformat(),
            "time_ago": _format_time_ago(job.completed_at)
        })

    return {"activity_feed": activity_feed}


@router.get("/activity/stats")
async def get_system_stats(db: Session = Depends(get_db)):
    """
    Get system-wide stats for social proof.

    Shows platform is active and growing.
    """
    now = datetime.now()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    # Jobs running RIGHT NOW
    jobs_running_now = db.query(Job).filter(Job.status == 'running').count()

    # Nodes online RIGHT NOW
    nodes_online_now = db.query(Node).filter(Node.status == 'online').count()

    # Jobs completed today
    jobs_completed_today = db.query(Job).filter(
        Job.status == 'completed',
        Job.completed_at >= today_start
    ).count()

    # Total jobs all time
    total_jobs_all_time = db.query(Job).count()

    # Total users
    total_users = db.query(User).count()

    return {
        "jobs_running_now": jobs_running_now,
        "nodes_online_now": nodes_online_now,
        "jobs_completed_today": jobs_completed_today,
        "total_jobs_all_time": total_jobs_all_time,
        "total_users": total_users,
        "timestamp": now.isoformat()
    }


@router.get("/testimonials")
async def get_testimonials(
    featured_only: bool = False,
    db: Session = Depends(get_db)
):
    """Get user testimonials for social proof."""
    query = db.query(Testimonial).filter(Testimonial.is_verified == True)

    if featured_only:
        query = query.filter(Testimonial.is_featured == True)

    testimonials = query.order_by(Testimonial.display_order).all()

    return {
        "testimonials": [
            {
                "quote": t.quote,
                "author": t.author_name,
                "title": t.author_title,
                "company": t.author_company,
                "avatar_url": t.avatar_url,
                "verified": t.is_verified
            }
            for t in testimonials
        ]
    }


def _format_time_ago(dt: datetime) -> str:
    """Format time as '2 minutes ago'."""
    diff = datetime.now() - dt
    seconds = diff.total_seconds()

    if seconds < 60:
        return "just now"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} minute{'s' if minutes != 1 else ''} ago"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} hour{'s' if hours != 1 else ''} ago"
    else:
        days = int(seconds / 86400)
        return f"{days} day{'s' if days != 1 else ''} ago"
```

---

### Phase 3: Frontend Landing Page (2 days)

**File: `frontend/src/components/LandingPage.tsx`**

```typescript
import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Zap, Users, Server, TrendingUp } from 'lucide-react';

interface ActivityItem {
  user: string;
  action: string;
  duration_minutes: number;
  time_ago: string;
}

interface SystemStats {
  jobs_running_now: number;
  nodes_online_now: number;
  jobs_completed_today: number;
  total_users: number;
}

interface Testimonial {
  quote: string;
  author: string;
  title: string;
  company: string;
  avatar_url: string;
}

export const LandingPage: React.FC = () => {
  const [activity, setActivity] = useState<ActivityItem[]>([]);
  const [stats, setStats] = useState<SystemStats | null>(null);
  const [testimonials, setTestimonials] = useState<Testimonial[]>([]);

  useEffect(() => {
    fetchData();

    // Refresh every 10 seconds
    const interval = setInterval(fetchData, 10000);
    return () => clearInterval(interval);
  }, []);

  const fetchData = async () => {
    // Fetch activity feed
    const activityRes = await fetch('/api/v1/activity/live');
    const activityData = await activityRes.json();
    setActivity(activityData.activity_feed);

    // Fetch stats
    const statsRes = await fetch('/api/v1/activity/stats');
    const statsData = await statsRes.json();
    setStats(statsData);

    // Fetch testimonials
    const testimonialsRes = await fetch('/api/v1/testimonials?featured_only=true');
    const testimonialsData = await testimonialsRes.json();
    setTestimonials(testimonialsData.testimonials);
  };

  return (
    <div className="space-y-12">
      {/* Hero */}
      <div className="text-center space-y-4">
        <h1 className="text-5xl font-bold">
          💻 Distributed Computing for Everyone
        </h1>
        <p className="text-xl text-gray-600">
          Share your idle CPU. Earn credits. Run faster.
        </p>

        {/* Live stats */}
        {stats && (
          <div className="flex justify-center gap-8 mt-8">
            <div className="flex items-center gap-2">
              <Zap className="w-5 h-5 text-yellow-500" />
              <div>
                <div className="text-2xl font-bold">{stats.jobs_running_now}</div>
                <div className="text-sm text-gray-600">jobs running now</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Server className="w-5 h-5 text-green-500" />
              <div>
                <div className="text-2xl font-bold">
                  {stats.nodes_online_now.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">nodes online</div>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <Users className="w-5 h-5 text-blue-500" />
              <div>
                <div className="text-2xl font-bold">
                  {stats.total_users.toLocaleString()}
                </div>
                <div className="text-sm text-gray-600">users</div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Live activity feed */}
      <Card className="p-6">
        <h2 className="text-2xl font-bold mb-4 flex items-center gap-2">
          🔥 Live Activity Feed
          <Badge variant="destructive" className="animate-pulse">LIVE</Badge>
        </h2>

        <div className="space-y-2 max-h-64 overflow-y-auto">
          {activity.slice(0, 10).map((item, idx) => (
            <div key={idx} className="flex items-center justify-between py-2 border-b">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                  {item.user[0]}
                </div>
                <div>
                  <span className="font-medium">{item.user}</span>
                  {' '}
                  <span className="text-gray-600">{item.action}</span>
                  {' '}
                  <span className="text-sm text-gray-500">
                    ({item.duration_minutes} min)
                  </span>
                </div>
              </div>
              <div className="text-sm text-gray-500">
                {item.time_ago}
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Testimonials */}
      <div className="space-y-6">
        <h2 className="text-3xl font-bold text-center">⭐ What Users Say</h2>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {testimonials.map((testimonial, idx) => (
            <Card key={idx} className="p-6">
              <div className="space-y-4">
                <p className="text-lg italic">"{testimonial.quote}"</p>

                <div className="flex items-center gap-3">
                  <img
                    src={testimonial.avatar_url}
                    alt={testimonial.author}
                    className="w-12 h-12 rounded-full"
                  />
                  <div>
                    <div className="font-semibold">{testimonial.author}</div>
                    <div className="text-sm text-gray-600">
                      {testimonial.title}
                    </div>
                    <div className="text-sm text-gray-500">
                      {testimonial.company}
                    </div>
                  </div>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>
    </div>
  );
};
```

---

## 👥 FEATURE 111: TEAM WORKSPACES & COLLABORATION

**Goal:** Enable team plans at $299/month for 10x revenue

### Phase 1: Database Schema (1 day)

```sql
-- Teams table
CREATE TABLE teams (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    slug VARCHAR(50) UNIQUE NOT NULL,  -- 'acme-corp-ml'
    credit_pool INT DEFAULT 0,
    plan VARCHAR(20) DEFAULT 'free',  -- 'free', 'team', 'enterprise'
    max_members INT DEFAULT 5,
    stripe_customer_id VARCHAR(100),  -- For billing
    stripe_subscription_id VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Team members
CREATE TABLE team_members (
    id SERIAL PRIMARY KEY,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    user_id INT REFERENCES users(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,  -- 'admin', 'member', 'viewer'
    joined_at TIMESTAMP DEFAULT NOW(),
    UNIQUE(team_id, user_id)
);

-- Team invitations
CREATE TABLE team_invitations (
    id SERIAL PRIMARY KEY,
    team_id INT REFERENCES teams(id) ON DELETE CASCADE,
    email VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL,
    invited_by INT REFERENCES users(id),
    token VARCHAR(64) UNIQUE NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    accepted_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Add team_id to jobs
ALTER TABLE jobs ADD COLUMN team_id INT REFERENCES teams(id);

-- Indexes
CREATE INDEX idx_team_members_team ON team_members(team_id);
CREATE INDEX idx_team_members_user ON team_members(user_id);
CREATE INDEX idx_jobs_team ON jobs(team_id);
```

---

### Phase 2: Backend API (3 days)

**File: `src/api/teams.py`**

```python
"""
Team Workspaces API

Endpoints:
- POST /teams - Create team
- GET /teams/{team_id} - Get team details
- POST /teams/{team_id}/invite - Invite member
- POST /teams/{team_id}/accept-invite - Accept invitation
- DELETE /teams/{team_id}/members/{user_id} - Remove member
- PUT /teams/{team_id}/upgrade - Upgrade plan
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
import secrets
from datetime import datetime, timedelta

from src.database.connection import get_db
from src.database.models import Team, TeamMember, TeamInvitation, User, Job
from src.api.auth import get_current_user
from src.utils.email import send_team_invitation_email

router = APIRouter()


# Pricing tiers
PRICING_TIERS = {
    "free": {
        "price": 0,
        "max_members": 3,
        "monthly_credits": 500
    },
    "team": {
        "price": 299,  # $299/month
        "max_members": 10,
        "monthly_credits": 50000
    },
    "enterprise": {
        "price": 999,  # $999/month
        "max_members": 100,
        "monthly_credits": 250000
    }
}


class CreateTeamRequest(BaseModel):
    name: str
    slug: str


class InviteMemberRequest(BaseModel):
    email: EmailStr
    role: str = "member"


@router.post("/teams")
async def create_team(
    request: CreateTeamRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new team."""

    # Check if slug is available
    existing = db.query(Team).filter(Team.slug == request.slug).first()
    if existing:
        raise HTTPException(400, "Team slug already taken")

    # Create team
    team = Team(
        name=request.name,
        slug=request.slug,
        credit_pool=PRICING_TIERS["free"]["monthly_credits"],
        plan="free",
        max_members=PRICING_TIERS["free"]["max_members"]
    )
    db.add(team)
    db.flush()

    # Add creator as admin
    membership = TeamMember(
        team_id=team.id,
        user_id=current_user.id,
        role="admin"
    )
    db.add(membership)
    db.commit()

    return {
        "team_id": team.id,
        "name": team.name,
        "slug": team.slug,
        "invite_url": f"/teams/{team.slug}/join",
        "plan": team.plan,
        "credit_pool": team.credit_pool
    }


@router.get("/teams/{team_id}")
async def get_team(
    team_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get team details."""

    # Check membership
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id
    ).first()

    if not membership:
        raise HTTPException(403, "Not a member of this team")

    team = db.query(Team).filter(Team.id == team_id).first()

    # Get all members
    members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).all()

    member_details = []
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()

        # Count jobs this month
        month_start = datetime.now().replace(day=1, hour=0, minute=0, second=0)
        jobs_this_month = db.query(Job).filter(
            Job.owner_id == user.id,
            Job.team_id == team_id,
            Job.created_at >= month_start
        ).count()

        member_details.append({
            "user_id": user.id,
            "username": user.username,
            "role": m.role,
            "joined_at": m.joined_at.isoformat(),
            "jobs_this_month": jobs_this_month
        })

    # Team stats
    total_jobs = db.query(Job).filter(Job.team_id == team_id).count()

    return {
        "team_id": team.id,
        "name": team.name,
        "slug": team.slug,
        "plan": team.plan,
        "credit_pool": team.credit_pool,
        "max_members": team.max_members,
        "members": member_details,
        "member_count": len(members),
        "total_jobs": total_jobs
    }


@router.post("/teams/{team_id}/invite")
async def invite_member(
    team_id: int,
    request: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Invite someone to join the team."""

    # Check if current user is admin
    membership = db.query(TeamMember).filter(
        TeamMember.team_id == team_id,
        TeamMember.user_id == current_user.id,
        TeamMember.role == "admin"
    ).first()

    if not membership:
        raise HTTPException(403, "Only team admins can invite members")

    team = db.query(Team).filter(Team.id == team_id).first()

    # Check if team has space
    current_members = db.query(TeamMember).filter(
        TeamMember.team_id == team_id
    ).count()

    if current_members >= team.max_members:
        raise HTTPException(
            400,
            f"Team is full ({current_members}/{team.max_members}). Upgrade plan to add more members."
        )

    # Check if user already member
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        existing_membership = db.query(TeamMember).filter(
            TeamMember.team_id == team_id,
            TeamMember.user_id == existing_user.id
        ).first()

        if existing_membership:
            raise HTTPException(400, "User is already a team member")

    # Create invitation
    token = secrets.token_urlsafe(32)
    invitation = TeamInvitation(
        team_id=team_id,
        email=request.email,
        role=request.role,
        invited_by=current_user.id,
        token=token,
        expires_at=datetime.now() + timedelta(days=7)
    )
    db.add(invitation)
    db.commit()

    # Send email
    send_team_invitation_email(
        to_email=request.email,
        team_name=team.name,
        inviter_name=current_user.username,
        role=request.role,
        invite_link=f"/teams/join/{token}"
    )

    return {
        "message": f"Invitation sent to {request.email}",
        "expires_at": invitation.expires_at.isoformat()
    }


@router.post("/teams/join/{token}")
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Accept team invitation."""

    # Find invitation
    invitation = db.query(TeamInvitation).filter(
        TeamInvitation.token == token,
        TeamInvitation.accepted_at.is_(None)
    ).first()

    if not invitation:
        raise HTTPException(404, "Invitation not found or already used")

    # Check expiration
    if invitation.expires_at < datetime.now():
        raise HTTPException(400, "Invitation has expired")

    # Check email matches
    if invitation.email != current_user.email:
        raise HTTPException(
            400,
            f"This invitation is for {invitation.email}, but you're logged in as {current_user.email}"
        )

    # Add to team
    membership = TeamMember(
        team_id=invitation.team_id,
        user_id=current_user.id,
        role=invitation.role
    )
    db.add(membership)

    # Mark invitation as accepted
    invitation.accepted_at = datetime.now()

    db.commit()

    team = db.query(Team).filter(Team.id == invitation.team_id).first()

    return {
        "message": f"Welcome to {team.name}!",
        "team_id": team.id,
        "team_name": team.name,
        "your_role": invitation.role
    }
```

---

### Phase 3: Frontend Team Dashboard (3 days)

**File: `frontend/src/components/TeamDashboard.tsx`**

```typescript
import React, { useEffect, useState } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Users, Mail, Crown, UserPlus } from 'lucide-react';

interface TeamMember {
  user_id: number;
  username: string;
  role: string;
  joined_at: string;
  jobs_this_month: number;
}

interface Team {
  team_id: number;
  name: string;
  slug: string;
  plan: string;
  credit_pool: number;
  max_members: number;
  member_count: number;
  members: TeamMember[];
  total_jobs: number;
}

export const TeamDashboard: React.FC<{ teamId: number }> = ({ teamId }) => {
  const [team, setTeam] = useState<Team | null>(null);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviting, setInviting] = useState(false);

  useEffect(() => {
    fetchTeam();
  }, [teamId]);

  const fetchTeam = async () => {
    const response = await fetch(`/api/v1/teams/${teamId}`, {
      headers: {
        'X-API-Key': localStorage.getItem('api_key') || ''
      }
    });
    const data = await response.json();
    setTeam(data);
  };

  const inviteMember = async () => {
    if (!inviteEmail) return;

    setInviting(true);
    try {
      const response = await fetch(`/api/v1/teams/${teamId}/invite`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': localStorage.getItem('api_key') || ''
        },
        body: JSON.stringify({
          email: inviteEmail,
          role: 'member'
        })
      });

      if (response.ok) {
        alert('Invitation sent!');
        setInviteEmail('');
      } else {
        const error = await response.json();
        alert(error.detail);
      }
    } finally {
      setInviting(false);
    }
  };

  if (!team) {
    return <div>Loading...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <Card className="p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">🏢 {team.name}</h1>
            <p className="text-gray-600 mt-1">Team workspace</p>
          </div>

          <div className="text-right">
            <div className="text-2xl font-bold">{team.credit_pool.toLocaleString()}</div>
            <div className="text-sm text-gray-600">credits available</div>
          </div>
        </div>

        <div className="mt-6 flex gap-4">
          <Badge variant="outline" className="text-sm">
            Plan: {team.plan}
          </Badge>
          <Badge variant="outline" className="text-sm">
            {team.member_count}/{team.max_members} members
          </Badge>
          <Badge variant="outline" className="text-sm">
            {team.total_jobs} total jobs
          </Badge>
        </div>
      </Card>

      {/* Members */}
      <Card className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-bold flex items-center gap-2">
            <Users className="w-5 h-5" />
            Team Members
          </h2>

          {team.member_count < team.max_members && (
            <div className="flex gap-2">
              <Input
                placeholder="email@example.com"
                value={inviteEmail}
                onChange={(e) => setInviteEmail(e.target.value)}
                className="w-64"
              />
              <Button onClick={inviteMember} disabled={inviting}>
                <UserPlus className="w-4 h-4 mr-2" />
                Invite
              </Button>
            </div>
          )}
        </div>

        <div className="space-y-3">
          {team.members.map((member) => (
            <div
              key={member.user_id}
              className="flex items-center justify-between p-4 border rounded-lg"
            >
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-white font-bold">
                  {member.username[0].toUpperCase()}
                </div>

                <div>
                  <div className="font-medium flex items-center gap-2">
                    {member.username}
                    {member.role === 'admin' && (
                      <Crown className="w-4 h-4 text-yellow-500" />
                    )}
                  </div>
                  <div className="text-sm text-gray-600">
                    {member.role} · Joined {new Date(member.joined_at).toLocaleDateString()}
                  </div>
                </div>
              </div>

              <div className="text-right">
                <div className="font-semibold">{member.jobs_this_month}</div>
                <div className="text-sm text-gray-600">jobs this month</div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      {/* Upgrade prompt */}
      {team.plan === 'free' && (
        <Card className="p-6 bg-gradient-to-r from-blue-50 to-purple-50 border-blue-200">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-lg font-bold">Upgrade to Team Plan</h3>
              <p className="text-gray-600 mt-1">
                Get 10 seats, 50,000 credits/month, priority queue, and more
              </p>
            </div>

            <Button size="lg" className="bg-gradient-to-r from-blue-500 to-purple-500">
              Upgrade for $299/month
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
};
```

---

## 📅 IMPLEMENTATION TIMELINE

### Week 1-2: Feature 108 (Templates)
- **Days 1-2:** Database + Backend API
- **Days 3-5:** Frontend components
- **Day 6:** Testing
- **Day 7:** Deploy to production

### Week 2-3: Feature 110 (Progress Visualization)
- **Days 1-2:** WebSocket backend
- **Days 3-5:** Frontend components
- **Day 6:** Testing
- **Day 7:** Deploy

### Week 3-4: Feature 109 (Social Proof)
- **Days 1-2:** Backend API
- **Days 3-4:** Frontend landing page
- **Day 5:** Testing
- **Days 6-7:** Deploy + monitor conversion rate

### Week 4-6: Feature 111 (Teams)
- **Days 1-2:** Database schema
- **Days 3-5:** Backend API
- **Days 6-10:** Frontend dashboard
- **Days 11-12:** Stripe integration for billing
- **Days 13-14:** Testing + deploy

---

## ✅ SUCCESS METRICS

Track these metrics to measure success:

### Feature 108 (Templates):
- ✅ Time to first job: Target <60 seconds
- ✅ Activation rate: Target 70%
- ✅ Template usage: >80% of new users

### Feature 110 (Progress):
- ✅ User retention on job page: >2 minutes
- ✅ Job completion rate: >90%
- ✅ WebSocket connection stability: >99%

### Feature 109 (Social Proof):
- ✅ Landing page conversion: 3x improvement
- ✅ Sign-up rate: 5% → 15%
- ✅ Testimonial click-through: >10%

### Feature 111 (Teams):
- ✅ Free → Team conversion: >10%
- ✅ MRR growth: $0 → $10K in 2 months
- ✅ Team size: Average 5 members

---

## 🚀 DEPLOYMENT CHECKLIST

Before deploying each feature:

- [ ] All tests passing
- [ ] Database migrations tested on staging
- [ ] Frontend builds without errors
- [ ] WebSocket connections tested under load
- [ ] API rate limits configured
- [ ] Monitoring dashboards created
- [ ] Rollback plan documented
- [ ] Feature flag enabled for 10% of users first
- [ ] Error tracking configured (Sentry)
- [ ] Performance baseline measured

---

**Total Implementation Time:** 4-6 weeks
**Expected Business Impact:** 10x improvement in activation, 3x conversion, $50K MRR in 6 months

