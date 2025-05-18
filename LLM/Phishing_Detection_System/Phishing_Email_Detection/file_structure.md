
#### Proposed File Structure:


| Function Type             | Example                                | Location                       | Why                                                     |
| ------------------------- | -------------------------------------- | ------------------------------ | ------------------------------------------------------- |
| **LLM API Call**          | `client.messages.create()`             | `services/anthropic_client.py` | Encapsulates API access logic, testable and replaceable |
| **Parsing LLM Output**    | Extract verdict, confidence, reasoning | `utils/parser.py`              | Reusable, isolated from UI                              |
| **Enrichment Functions**  | Enrich URLs, hashes, etc.              | `services/enrichment.py`       | Keeps threat intelligence logic modular                 |
| **Data Preprocessing**    | Clean inputs, normalize email body     | `utils/ioc_utils.py`           | Focused on data shaping                                 |
| **Reusable Streamlit UI** | Custom layout, display cards           | `components/`                  | Modular, simplifies `app.py`                            |
| **Styling**               | CSS code                               | `styles/custom.css`            | Clean and maintainable presentation                     |

