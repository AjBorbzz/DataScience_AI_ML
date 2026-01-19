from scripts.verse_guard import extract_refs, validate_refs
from scripts.context_builder import build_context
from fake_llm import fake_llm_valid, fake_llm_invalid
from fixtures_passage import PASSAGES

def run_test(llm_fn, label):
    context, allowed_refs = build_context(PASSAGES)

    answer = llm_fn(
        system_prompt="TEST",
        context=context,
        question="money"
    )

    found = extract_refs(answer)
    invalid = validate_refs(found, allowed_refs)

    print("=" * 60)
    print(label)
    print("Allowed refs:", allowed_refs)
    print("Found refs:", found)

    if invalid:
        print("[BLOCKED] Invalid refs detected:", invalid)
    else:
        print("[PASS] All refs valid")

def main():
    run_test(fake_llm_valid, "VALID RESPONSE TEST")
    run_test(fake_llm_invalid, "INVALID RESPONSE TEST")

if __name__ == "__main__":
    main()
