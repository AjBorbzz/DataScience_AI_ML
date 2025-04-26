
---

### 🚀 1. **Use `@st.cache_data` and `@st.cache_resource` Wisely**
Cache expensive computations or data loading operations.

#### ✅ For data (like Pandas/NumPy):
```python
@st.cache_data
def load_data():
    df = pd.read_csv("large_dataset.csv")
    return df
```

#### ✅ For models, APIs, or database connections:
```python
@st.cache_resource
def load_model():
    return joblib.load("model.pkl")
```

> ⚠️ Don't cache functions that depend on frequently changing inputs unless you set `ttl=` (time-to-live).

---

### 🧠 2. **Avoid Recomputing in the Main Script**
Streamlit runs top-to-bottom on every interaction. Move heavy logic **inside functions** and cache them.

```python
def run_inference(model, input_data):
    return model.predict(input_data)
```

---

### 📦 3. **Reduce UI Rerenders**
Use **`st.session_state`** to persist values and avoid unnecessary reruns.

```python
if 'data_loaded' not in st.session_state:
    st.session_state['data_loaded'] = load_data()
```

---

### 🧼 4. **Minimize DOM Elements**
Avoid rendering big tables, images, or charts that don’t need to update.

#### ✅ Use `st.empty()` to update only the part of UI that changes:
```python
placeholder = st.empty()
for i in range(100):
    placeholder.text(f"Step {i}")
```

---

### 🔁 5. **Control Reruns with Widgets**
Widgets trigger reruns. Use `key=` wisely, and group them in forms to prevent partial reruns:

```python
with st.form("inputs"):
    input_val = st.text_input("Input:")
    submitted = st.form_submit_button("Run")
```

---

### 📉 6. **Optimize Data Size**
- Filter or aggregate large datasets before showing them.
- Don’t send 100k rows to `st.dataframe()` — use `st.data_editor()` or `df.head()`.

---

### 🖼️ 7. **Lazy Load Heavy Visuals**
- Use `st.image(..., use_column_width="always")` to avoid layout shifts.
- Avoid showing many images at once — use pagination or collapsible sections.

---

### 🛜 8. **Use Async APIs (Advanced)**
If you're calling APIs, use `async def` + `asyncio`, or offload to background threads.

---

### ⚙️ 9. **Deploy on Streamlit Community Cloud or a Fast Server**
Make sure you're on a fast-enough backend:
- Use **Streamlit Cloud**, **Render**, or **EC2/GCP**
- Avoid underpowered free-tier VMs for data-heavy apps

---

### 🧪 10. **Profile Bottlenecks**
Use logging or `time` to identify slow parts:
```python
import time
start = time.time()
# your logic
st.write("⏱️ Took:", time.time() - start, "s")
```

---
