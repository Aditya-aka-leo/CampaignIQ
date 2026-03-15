"""
Quick utility to test each layer individually.
Usage:
    python test_layers.py l3
    python test_layers.py l1
    python test_layers.py l2
    python test_layers.py l4
    python test_layers.py all
"""
import asyncio
import json
import sys

SAMPLE_ASSET = "Earn 4.5% AER with TrustBank savings. Your money, working harder for you."
CHANNEL = "email"
SEGMENT = "retail_savings"


async def test_l1():
    print("\n── L1: Performance Prediction ──")
    from layers.l1 import run_l1
    result = await run_l1(SAMPLE_ASSET, CHANNEL, SEGMENT)
    print(json.dumps(result, indent=2))
    return result


async def test_l2():
    print("\n── L2: Brand Consistency ──")
    from layers.l2 import run_l2
    result = await run_l2(SAMPLE_ASSET)
    print(json.dumps(result, indent=2))
    return result


async def test_l3():
    print("\n── L3: Market Context (web search — may take ~70s) ──")
    from layers.l3 import run_l3
    result = await run_l3(SAMPLE_ASSET, CHANNEL)
    print(json.dumps(result, indent=2))
    return result


async def test_l4(l1=None, l2=None, l3=None):
    print("\n── L4: Creative Synthesis ──")
    from layers.l4 import run_l4
    result = await run_l4(SAMPLE_ASSET, l1, l2, l3)
    print(json.dumps(result, indent=2))
    return result


async def test_all():
    print("Running L1, L2, L3 in parallel...")
    l1, l2, l3 = await asyncio.gather(
        test_l1(), test_l2(), test_l3()
    )
    await test_l4(l1, l2, l3)


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "l3"

    if target == "l1":
        asyncio.run(test_l1())
    elif target == "l2":
        asyncio.run(test_l2())
    elif target == "l3":
        asyncio.run(test_l3())
    elif target == "l4":
        asyncio.run(test_l4())
    elif target == "all":
        asyncio.run(test_all())
    else:
        print(f"Unknown target '{target}'. Use: l1 | l2 | l3 | l4 | all")
