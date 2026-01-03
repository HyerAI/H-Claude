### **The Agentic Framework**

**GOAL:**

1. Capture the User's vision clearly.  
2. Research *only* the features and tech stack necessary to deliver that specific vision.  
3. Create a plan that executes the vision without adding unrequested "bloat."  
4. Execute tasks sequentially until the Roadmap is complete.

**PLANNING RULES:**

1. **Strict Northstar Alignment:** We map features directly to the Northstar goals. We do not add "standard industry features" unless they serve a specific goal in the user's request.  
2. **Validated Tech Stack:** The stack must be researched to ensure it supports the specific requirements (compatibility, performance, 2026 standards).  
3. **Dependency Order:** Plans must be ordered logically with blockers identified.

**AGENTS::**

* PO\[x\]= Product Owner Agent  
* ORCA\[x\] \= Orchestration agent  
* RCH\[x\] \= Researcher agent  
* ARC\[x\] \= Architect agent  
* WR\[x\]= Worker Agent  
* QA\[x\]= QA Agent  
* VA\[x\]= Validator Agent

**DOCS::**

* RM \= ROADMAP  
* NS \= NORTHSTAR

---

#### **Phase 1: Discovery & Definition (Northstar)**

* **Step 1:** **User** ↔ **PO\[1\]**  
  * **Action:** Discuss the idea. PO\[1\] focuses on defining the specific problem and the desired solution boundaries.  
  * **Output:** **NS (Northstar)** document defining "In-Scope" goals and "Out-of-Scope" limitations.  
* **Step 2:** **User** ↔ **PO\[1\]**  
  * **Action:** Feedback loop to confirm the NS matches the user's intent exactly.  
  * **Output:** Approved **NS**.

### **Phase 2: Targeted Research & Validation**

* **Step 3:** **PO\[1\]** → **RCH\[1\]**  
  * **Action:**  
    1. **Requirement Mapping:** Identify the specific technical features required to achieve the Approved NS. *Filter out generic features not requested.*  
    2. **Tech Selection:** Research the best Tech Stack to support *only* those specific features.  
  * **Output:** **Feasibility Report** (Targeted Feature List \+ Recommended Stack).  
* **Step 4:** **RCH\[1\]** → **VA\[1\]**  
  * **Action:** Validate that the proposed features and stack cover 100% of the Northstar without unnecessary complexity (bloat).  
  * **Output:** Validated Stack & Scope.

### **Phase 3: Architecture & Roadmap**

* **Step 5:** **PO\[1\]** \+ **RCH\[1\]** → **ARC\[1\]**  
  * **Action:** Create a high-level Master Roadmap based on the Validated Scope.  
  * **Output:** **RM (Roadmap)** divided into logical Phases.

### **Phase 4: Granular Planning (The Resolution Process)**

*This phase progressively "denoises" the Vision into executable Reality, ensuring every plan is anchored in the "Immutable Past" (existing code).*

* **Step 6: Phase Definition** (Future Strategy \+ Past Reality → Phase Roadmap)  
  * **Actors:** **ARC\[1\]** \+ **ORCA\[1\]**  
  * **Inputs:** **Master Roadmap (RM)** (The Future) \+ **Current Codebase Analysis** (The Past/Bedrock).  
  * **Action:** Analyze the current state of the codebase ("The Bedrock") to ensure the next logical phase from the **RM** is architecturally viable. Expand this phase into a dedicated **Phase Roadmap**.  
  * **Validation (VA\[1\]):** **Simulation Check.** Does this Phase Roadmap align with the **NS** (Vision) while respecting the constraints of the **Current Codebase** (Reality)?  
  * **Output:** **Phase Roadmap** (The Locked Present).  
* **Step 7: Task Planning** (Phase Roadmap → Task Plan)  
  * **Actors:** **ORCA\[1\]**  
  * **Action:** Break down the **Phase Roadmap** into a **Task Plan** (distinct, high-level deliverables). This defines the "Physics" of the phase—how the pieces connect before we build them.  
  * **Validation (VA\[1\]):** **Scope & Physics Check.** Does every item trace back to the Phase Roadmap without added bloat? Do the tasks logically fit the established architecture?  
  * **Output:** **Task Plan**.  
* **Step 8: Ticket Creation** (Task Plan → Sub-Task Tickets)  
  * **Actors:** **ORCA\[1\]** \+ **PO\[1\]**  
  * **Action:** Decompose items in the **Task Plan** into actionable **Sub-Task Tickets**.  
  * **Content:**  
    * *Context:* **Triangulated Context** (The specific Goal \+ The specific Existing Files/Code to modify).  
    * *Specs:* Requirements, Input/Output definitions, Acceptance Criteria.  
  * **Validation (VA\[1\]):** **Resolution Check.** Is the ticket small enough for a Worker to execute deterministically? Is the context "Bedrock" provided?  
  * **Output:** **Sub-Task Ticket Queue**.

### **Phase 5: The Execution Loop (Rendering Reality)**

*The continuous cycle of closing the gap between the Code (Past) and the Vision (Future).*

* **Step 9: The Rolling Focus Loop**  
  * **WR\[1\] (Execution):** Reads the **Ticket** (Present Plan) and the **Existing Code** (Immutable Past). Executes the task to render the update.  
  * **QA\[1\] (Reality Check):** Tests the output against the specific ticket requirements. "Does the code function as planned?"  
  * **VA\[1\] (Vision Check \- Lookahead):** Validates the result against the **Task Plan** and **NS**. "Does this new code block the future User Experience?"  
  * **ORCA\[1\] (Completion):** Marks the ticket Complete and updates the Context for the next ticket.  
* **Step 10: Loop Maintenance**  
  * **ORCA\[1\]** checks queue status.  
  * *If Tickets remain:* **Repeat Loop** (Feeding the new "Past" into the next ticket).  
  * *If Queue empty:* Verify Phase Completion → Trigger **Step 6** for the next Phase (increasing resolution for the next slice of the Roadmap).

### **Summary of Hierarchy (The Diffusion Stack)**

1. **Northstar (NS):** The **Future** (User Vision/Goal).  
2. **Master Roadmap (RM):** The **Sketch** (High-level Strategy).  
3. **Phase Roadmap:** The **Structure** (Tactical Plan per phase, anchored in Codebase).  
4. **Task Plan:** The **Blueprint** (Specific Deliverables).  
5. **Sub-Task Ticket:** The **Instruction** (Context-rich work unit).  
6. **Code:** The **Immutable Past** (The Bedrock we build upon).

---

---

# **🌲 The Diffusion Development Philosophy**

**Predictable State & Rolling Diffusion**

**"We do not guess the future. We simulate it, lock the foundation, and render the reality one phase at a time."**   
**“The Plan is the Code we build; The Future is the User Vision we chase.”**

---

### **1\. The Core Objective: Determinism from Probability**

The fundamental challenge of generative development is that Intelligence is probabilistic (creative/random), but Engineering is deterministic (rigid/predictable).

To build robust systems, we must impose **Rigid State Containers** upon the creative process. We do not ask the system to "create" in a vacuum; we ask it to **solve the differential** between two known states.

* **The Problem:** Creation without constraint creates entropy (hallucinations, drift, bugs).  
* **The Solution:** The system never works on a blank canvas. It works inside a **Triangulated Context**:  
  1. **The Immutable Past:** The Code that actually exists (The Bedrock).  
  2. **The Locked Present (The Plan):** The specific technical specification we are building *right now*. This is the bridge.  
  3. **The Future Constraint (The Vision):** The Final Product Goal. This is not "next week's code"—it is the ultimate **User Experience** we are striving for. It is the gravitational pull that aligns the Plan.  
* **The Result:** The system is not "guessing"; it is **rendering**. It is closing the gap between the **Current Reality** (Past) and the **User Vision** (Future), using the **Plan** (Present) as the execution tool.

---

### **2\. The Workflow: Rolling Diffusion**

We reject the "Big Bang" waterfall method, and we reject "Blind Agile" coding. We adopt a **Rolling Focus** model—a continuous process of increasing resolution.

#### **Stage 1: The Logic Tree (Structure over Syntax)**

We do not start with a user story. We start with **Causality**.

* **The Concept:** Before we define *what* it looks like, we define *how* it thinks.  
* **The Action:** We map the Flow of Logic.  
* **The Output:** A platform-agnostic map of cause-and-effect. If the logic is flawed, no amount of perfect code can save it.

#### **Stage 2: The Physics (The Simulation)**

Before building the features, we determine the **Physics** of the world they inhabit.

* **The Simulation:** We "run" the Logic Tree against our architectural constraints in the abstract.  
* **The Prediction:** We ask, "If we lay this foundation, will it support the weight of the User Vision?"  
* **The Fix:** We solve architectural contradictions in the planning phase, treating the *Plan* as the first prototype, not the Code.

#### **Stage 3: The Lookahead Loop (The Dual Engine)**

This is the heartbeat of Diffusion Development. We operate on two temporal tracks simultaneously:

| Track A: The Reality (High Resolution) | Track B: The Horizon (Low Resolution) |
| :---- | :---- |
| **Execution:** Building the **Plan**. We are laying bricks, pouring concrete, writing logic. This is high-stakes, high-detail work. | **Navigation:** Aligning with the **Vision**. We are checking the map, verifying that the Plan we are building today actually leads to the User Experience we promised for the end. |

The Discipline of Lookahead:

When we plan the Current Phase, we explicitly validate it against the User Vision. We ask: "Does the technical decision I make today block the User Experience of the future?"

If Today's Code blocks Tomorrow's Vision, we change Today's Code. We do not wait for the Future to fail.

---

### **3\. The Resolution Process (Fuzzy to HD)**

This pipeline creates the **Diffusion Effect**—the gradual "denoising" of an idea into reality.

1. **The Noise (The Vision):** The raw User Goal. "I want a platform that does X." Infinite possibilities, high entropy.  
2. **The Sketch (Roadmap):** A low-resolution map of the journey.  
3. **The Wireframe (Simulation):** We verify the structural integrity. The "Physics" are locked.  
4. **The Blueprint (The Plan):** The resolution increases. We define the exact boundaries of the immediate step.  
5. **The Reality (The Code):** The resolution reaches Maximum. The idea has hardened into immutable fact.

---

### **4\. Summary: The Feedback Loop**

We exist in a constant state of calibration, looking **Backward** at Reality and **Forward** at Vision.

* **Looking Back (Reality Check):** "The foundation is poured. It is slightly different than the blueprint."  
* **Looking Forward (Vision Check):** "Does this new reality still allow us to achieve the User Goal?"  
* **Action:** "Adjust the Plan. Keep the Vision constant."

The Philosophy:

We clarify the picture loop by loop. The User Vision (The Future) is the destination. The Code (The Past) is where we stand. The Plan (The Present) is the step we take. We do not build the whole thing at once; we let the reality of the software diffuse into existence, layer by predictable layer.
