#!/usr/bin/env python3
"""Rename schema classes and files per V2-03 + CQ-01 audit findings.

This script:
1. Renames schema files via git mv
2. Updates class names, import paths, and local variables across the codebase
3. Regenerates schemas/__init__.py

Run from the repository root:
    python scripts/rename_schemas.py
"""

import re
import subprocess
import sys
from pathlib import Path

# ──────────────────────────────────────────────────────────────────────────────
# Complete rename mapping: OldClassName -> NewClassName
# Classes NOT in this map are left unchanged.
# ──────────────────────────────────────────────────────────────────────────────
RENAME_MAP = {
    # ── Category A: Opaque suffixed names ──
    "Add2": "AddOrderResponse",
    "Add2OrderAdded": "AddOrderResult",
    "Add2OrderAddedDescr": "AddOrderResultDescr",
    "Edit2": "EditOrderResponse",
    "Edit2OrderEdited": "EditOrderResult",
    "Edit2OrderEditedDescr": "EditOrderResultDescr",
    "Closed2": "GetClosedOrdersResponse",
    "Closed2ClosedOrders": "GetClosedOrdersResult",
    "Closed2ClosedOrdersClosed": "GetClosedOrdersResultEntries",
    "Open2": "GetOpenOrdersResponse",
    "Open2OpenOrders": "GetOpenOrdersResult",
    "Open2OpenOrdersOpen": "GetOpenOrdersResultEntries",
    "Balance2": "GetBalanceResponse",
    "Balanceex2": "GetExtendedBalanceResponse",
    "Balanceex2ExtendedBalance": "GetExtendedBalanceResult",
    "History2": "GetTradeHistoryResponse",
    "Info2": "GetAssetInfoResponse",
    "Info2Result": "GetAssetInfoResult",
    "Info3": "GetLedgersResponse",
    "Info3LedgersInfo": "GetLedgersResult",
    "Info3LedgersInfoLedger": "GetLedgersResultEntries",
    "Info4": "WithdrawalInfoRequest",
    "Info5": "WithdrawalInfoResponse",
    "Info5WithdrawalInfo": "WithdrawalInfoResult",
    "Methods2": "GetDepositMethodsResponse",
    "Query2": "GetOrdersInfoResponse",
    "Query2Result": "GetOrdersInfoResult",
    "Query3": "GetLedgersInfoResponse",
    "Query3Result": "GetLedgersInfoResult",
    "Recent2": "GetRecentDepositsResponse",
    "Recent2ResultType1": "GetRecentDepositsResultAlt",
    "Spread2": "GetRecentSpreadsResponse",
    "Spread2Result": "GetRecentSpreadsResult",
    "Ticker2": "GetTickerResponse",
    "Ticker2Result": "GetTickerResult",
    "Withdrawal2": "WithdrawFundsResponse",
    "Withdrawal2Result": "WithdrawFundsResult",
    "Addresses": "GetDepositAddressesRequest",
    "Addresses2": "GetDepositAddressesResponse",
    "Batchadd2": "BatchAddOrderResponse",
    "Batchadd2Result": "BatchAddOrderResult",
    "Batchadd2ResultOrdersItem": "BatchAddOrderResultItem",
    "Batchadd2ResultOrdersItemDescr": "BatchAddOrderResultItemDescr",
    "Withdrawal": "WithdrawFundsRequest",
    # ── Category B: Already descriptive — kept as-is (not in map) ──
    # ── Category C: Verbose Response200/Result/JsonBody/Data patterns ──
    "AddExportData": "AddExportRequest",
    "AddExportResponse200": "AddExportResponse",
    "AddExportResponse200Result": "AddExportResult",
    "AddStandardOrderRequestBody": "AddOrderRequest",
    "AllocateStrategyJsonBody": "AllocateStrategyRequest",
    "AllocateStrategyJsonBodyNonce": "AllocateStrategyRequestNonce",
    "AllocateStrategyResponse200": "AllocateStrategyResponse",
    "BatchCancelOpenOrdersRequestBody": "BatchCancelOrdersRequest",
    "BatchCancelOpenOrdersRequestBodyOrdersItem": "BatchCancelOrdersRequestItem",
    "CancelAllOrdersAfterData": "CancelAllOrdersAfterRequest",
    "CancelAllOrdersAfterResponse200": "CancelAllOrdersAfterResponse",
    "CancelAllOrdersAfterResponse200Result": "CancelAllOrdersAfterResult",
    "CancelAllOrdersResponse200": "CancelAllOrdersResponse",
    "CancelAllOrdersResponse200Result": "CancelAllOrdersResult",
    "CancelOpenOrderRequestBody": "CancelOrderRequest",
    "CancelWithdrawalResponse200": "CancelWithdrawalResponse",
    "CreateSubaccountData": "CreateSubaccountRequest",
    "CreateSubaccountResponse200": "CreateSubaccountResponse",
    "DeallocateStrategyJsonBody": "DeallocateStrategyRequest",
    "DeallocateStrategyJsonBodyNonce": "DeallocateStrategyRequestNonce",
    "DeallocateStrategyResponse200": "DeallocateStrategyResponse",
    "EditStandardOrderRequestBody": "EditOrderRequest",
    "ExportStatusData": "ExportStatusRequest",
    "ExportStatusResponse200": "ExportStatusResponse",
    "ExportStatusResponse200ResultItem": "ExportStatusResultItem",
    "GetAllocateStrategyStatusJsonBody": "GetAllocateStrategyStatusRequest",
    "GetAllocateStrategyStatusJsonBodyNonce": "GetAllocateStrategyStatusRequestNonce",
    "GetAllocateStrategyStatusResponse200": "GetAllocateStrategyStatusResponse",
    "GetAllocateStrategyStatusResponse200Result": "GetAllocateStrategyStatusResult",
    "GetDeallocateStrategyStatusJsonBody": "GetDeallocateStrategyStatusRequest",
    "GetDeallocateStrategyStatusJsonBodyNonce": (
        "GetDeallocateStrategyStatusRequestNonce"
    ),
    "GetDeallocateStrategyStatusResponse200": "GetDeallocateStrategyStatusResponse",
    "GetDeallocateStrategyStatusResponse200Result": "GetDeallocateStrategyStatusResult",
    "GetDespositMethodsRequestBody": "GetDepositMethodsRequest",
    "GetOpenPositionsData": "GetOpenPositionsRequest",
    "GetOpenPositionsResponse200": "GetOpenPositionsResponse",
    "GetOpenPositionsResponse200Result": "GetOpenPositionsResult",
    "GetOpenPositionsResponse200ResultAdditionalProperty": (
        "GetOpenPositionsResultEntry"
    ),
    "GetStatusOfRecentDepositsRequestBody": "GetRecentDepositsRequest",
    "GetStatusOfRecentWithdrawalsRequestBody": "GetRecentWithdrawalsRequest",
    "GetSystemStatusResponse200": "GetSystemStatusResponse",
    "GetSystemStatusResponse200Result": "GetSystemStatusResult",
    "GetTradableAssetPairsResponse200": "GetTradableAssetPairsResponse",
    "GetTradableAssetPairsResponse200Result": "GetTradableAssetPairsResult",
    "GetTradesInfoResponse200": "GetTradesInfoResponse",
    "GetTradesInfoResponse200Result": "GetTradesInfoResult",
    "GetWebsocketsTokenResponse200": "GetWebsocketsTokenResponse",
    "GetWebsocketsTokenResponse200Result": "GetWebsocketsTokenResult",
    "QueryOrdersInfoRequestBody": "QueryOrdersInfoRequest",
    "RemoveExportData": "RemoveExportRequest",
    "RemoveExportResponse200": "RemoveExportResponse",
    "RemoveExportResponse200Result": "RemoveExportResult",
    "RequestWithdrawalCancelationRequestBody": "CancelWithdrawalRequest",
    "RetrieveExportData": "RetrieveExportRequest",
    "RetrieveExportResponse200": "RetrieveExportResponse",
    "WalletTransferData": "WalletTransferRequest",
    "WalletTransferResponse200": "WalletTransferResponse",
    "WalletTransferResponse200Result": "WalletTransferResult",
    # Remaining response envelopes with descriptive-but-generic names
    "Depth": "OrderBookResponse",
    "DepthResult": "OrderBookResult",
    "Ohlc": "OhlcResponse",
    "Time": "ServerTimeResponse",
    "TimeServerTime": "ServerTime",
    "Trades": "RecentTradesResponse",
    "TradesResult": "RecentTradesResult",
    "Volume": "TradeVolumeResponse",
    "VolumeTradeVolume": "TradeVolumeResult",
    "VolumeTradeVolumeFees": "TradeVolumeFees",
    "VolumeTradeVolumeFeesMaker": "TradeVolumeFeesMaker",
    "TradeHistory": "GetTradeHistoryResult",
    "TradeHistoryTrades": "GetTradeHistoryResultTrades",
    # ── Category D: Deeply nested earn names (CQ-01) ──
    "ListAllocationsJsonBody": "ListAllocationsRequest",
    "ListAllocationsJsonBodyNonce": "ListAllocationsRequestNonce",
    "ListAllocationsResponse200": "ListAllocationsResponse",
    "ListAllocationsResponse200Result": "ListAllocationsResult",
    "ListAllocationsResponse200ResultItemsItem": "Allocation",
    "ListAllocationsResponse200ResultItemsItemAmountAllocated": "AllocationAmount",
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedBonding": (
        "AllocationBonding"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedBondingAllocationsItem": (
        "AllocationBondingEntry"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedExitQueue": (
        "AllocationExitQueue"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedExitQueueAllocationsItem": (
        "AllocationExitQueueEntry"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedPending": (
        "AllocationPending"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedTotal": "AllocationTotal",
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedUnbonding": (
        "AllocationUnbonding"
    ),
    "ListAllocationsResponse200ResultItemsItemAmountAllocatedUnbondingAllocationsItem": (
        "AllocationUnbondingEntry"
    ),
    "ListAllocationsResponse200ResultItemsItemPayout": "AllocationPayout",
    "ListAllocationsResponse200ResultItemsItemPayoutAccumulatedReward": (
        "AllocationAccumulatedReward"
    ),
    "ListAllocationsResponse200ResultItemsItemPayoutEstimatedReward": (
        "AllocationEstimatedReward"
    ),
    "ListAllocationsResponse200ResultItemsItemTotalRewarded": "AllocationTotalRewarded",
    "ListStrategiesJsonBody": "ListStrategiesRequest",
    "ListStrategiesJsonBodyNonce": "ListStrategiesRequestNonce",
    "ListStrategiesResponse200": "ListStrategiesResponse",
    "ListStrategiesResponse200Result": "ListStrategiesResult",
    "ListStrategiesResponse200ResultItemsItem": "EarnStrategy",
    "ListStrategiesResponse200ResultItemsItemAprEstimate": "EarnStrategyAprEstimate",
    "ListStrategiesResponse200ResultItemsItemAutoCompoundType0": (
        "EarnStrategyAutoCompoundDisabled"
    ),
    "ListStrategiesResponse200ResultItemsItemAutoCompoundType1": (
        "EarnStrategyAutoCompoundForced"
    ),
    "ListStrategiesResponse200ResultItemsItemAutoCompoundType2": (
        "EarnStrategyAutoCompoundOptional"
    ),
    "ListStrategiesResponse200ResultItemsItemLockTypeType0": "EarnStrategyLockFlex",
    "ListStrategiesResponse200ResultItemsItemLockTypeType1": "EarnStrategyLockBonded",
    "ListStrategiesResponse200ResultItemsItemLockTypeType2": "EarnStrategyLockTimed",
    "ListStrategiesResponse200ResultItemsItemLockTypeType3": "EarnStrategyLockInstant",
    "ListStrategiesResponse200ResultItemsItemYieldSourceType0": (
        "EarnStrategyYieldStaking"
    ),
    "ListStrategiesResponse200ResultItemsItemYieldSourceType1": (
        "EarnStrategyYieldOffChain"
    ),
}

# Classes that exist but are NOT renamed (for __init__.py regeneration)
KEEP_AS_IS = [
    "AccountBalance",
    "AccountTransferRequest",
    "AccountTransferResponse",
    "AccountTransferResult",
    "AssetInfo",
    "AssetPair",
    "AssetTickerInfo",
    "ClosedOrder",
    "Deposit",
    "DepositAddress",
    "DepositMethod",
    "ExtendedBalance",
    "FeeTierInfo",
    "LedgerEntry",
    "Lock",
    "OhlcResult",
    "OpenOrder",
    "OpenOrderOrderDescription",
    "OrderBook",
    "Trade",
]

# Multi-class files: filename -> list of classes
MULTI_CLASS_FILES = {
    "account_transfer": [
        "AccountTransferResponse",
        "AccountTransferResult",
        "AccountTransferRequest",
    ],
}


def to_snake_case(name: str) -> str:
    """Convert PascalCase to snake_case matching openapi-python-client.

    Handles letter-digit and digit-letter boundaries:
      Add2 -> add_2, Response200 -> response_200, Type0 -> type_0
    """
    s1 = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", name)
    s2 = re.sub("([a-z0-9])([A-Z])", r"\1_\2", s1)
    # Insert underscore at letter-digit and digit-letter boundaries
    s3 = re.sub("([a-zA-Z])([0-9])", r"\1_\2", s2)
    s4 = re.sub("([0-9])([a-zA-Z])", r"\1_\2", s3)
    return s4.lower()


def validate_mapping(schemas_dir: Path) -> dict:
    """Validate the rename mapping and return old_cls -> (old_mod, new_mod) dict."""
    info = {}
    errors = []

    for old_cls, new_cls in RENAME_MAP.items():
        old_mod = to_snake_case(old_cls)
        new_mod = to_snake_case(new_cls)
        info[old_cls] = (old_mod, new_mod)

        # Verify old file exists (skip multi-class file members)
        is_multi = any(old_cls in classes for classes in MULTI_CLASS_FILES.values())
        if not is_multi:
            old_file = schemas_dir / f"{old_mod}.py"
            if not old_file.exists():
                errors.append(f"  {old_file} does not exist for {old_cls}")

    # Check for collisions
    new_names = list(RENAME_MAP.values())
    if len(new_names) != len(set(new_names)):
        seen = set()
        for n in new_names:
            if n in seen:
                errors.append(f"  Collision: {n}")
            seen.add(n)

    new_mods = [to_snake_case(n) for n in new_names]
    if len(new_mods) != len(set(new_mods)):
        seen = set()
        for m in new_mods:
            if m in seen:
                errors.append(f"  Module collision: {m}")
            seen.add(m)

    if errors:
        print("Validation errors:")
        for e in errors:
            print(e)
        sys.exit(1)

    return info


def rename_files(schemas_dir: Path, info: dict) -> None:
    """Rename schema files via git mv."""
    for old_cls in RENAME_MAP:
        old_mod, new_mod = info[old_cls]
        if old_mod == new_mod:
            continue
        old_file = schemas_dir / f"{old_mod}.py"
        new_file = schemas_dir / f"{new_mod}.py"
        if old_file.exists():
            subprocess.run(["git", "mv", str(old_file), str(new_file)], check=True)
            print(f"  {old_mod}.py -> {new_mod}.py")


def update_file_contents(py_files: list, info: dict) -> None:
    """Update imports, class names, and local variables in all Python files."""
    # Sort by old class name length descending to avoid partial matches
    sorted_renames = sorted(RENAME_MAP.items(), key=lambda x: len(x[0]), reverse=True)

    # Build module replacement pairs (also sorted longest first)
    mod_replacements = []
    for old_cls, _new_cls in sorted_renames:
        old_mod, new_mod = info[old_cls]
        if old_mod != new_mod:
            mod_replacements.append((old_mod, new_mod))

    # Build class name regex patterns
    class_replacements = []
    for old_cls, new_cls in sorted_renames:
        pattern = re.compile(rf"\b{re.escape(old_cls)}\b")
        class_replacements.append((pattern, new_cls))

    for py_file in py_files:
        content = py_file.read_text()
        original = content

        # Replace module names in import paths
        for old_mod, new_mod in mod_replacements:
            # Handle: from .old_mod import  /  from ..schemas.old_mod import
            content = content.replace(f".{old_mod} import", f".{new_mod} import")

        # Replace class names (word-boundary aware)
        for pattern, new_cls in class_replacements:
            content = pattern.sub(new_cls, content)

        if content != original:
            py_file.write_text(content)
            print(f"  Updated {py_file}")


def regenerate_init(schemas_dir: Path, info: dict) -> None:
    """Regenerate schemas/__init__.py with updated imports and __all__."""
    # Build the full class -> module mapping
    cls_to_mod = {}

    # Classes that were renamed
    for old_cls, new_cls in RENAME_MAP.items():
        _, new_mod = info[old_cls]
        cls_to_mod[new_cls] = new_mod

    # Classes kept as-is
    for cls_name in KEEP_AS_IS:
        cls_to_mod[cls_name] = to_snake_case(cls_name)

    # Multi-class files
    for mod_name, classes in MULTI_CLASS_FILES.items():
        for cls_name in classes:
            cls_to_mod[cls_name] = mod_name

    # Group classes by module
    mod_to_classes = {}
    for cls_name, mod_name in cls_to_mod.items():
        mod_to_classes.setdefault(mod_name, []).append(cls_name)

    # Sort modules and classes
    sorted_mods = sorted(mod_to_classes.keys())

    lines = ['"""Contains all the data schemas used in requests and responses."""\n']

    for mod_name in sorted_mods:
        classes = sorted(mod_to_classes[mod_name])
        if len(classes) == 1:
            lines.append(f"from .{mod_name} import {classes[0]}")
        else:
            lines.append(f"from .{mod_name} import (")
            for cls_name in classes:
                lines.append(f"    {cls_name},")
            lines.append(")")

    # Generate __all__
    all_classes = sorted(cls_to_mod.keys())
    lines.append("")
    lines.append("__all__ = (")
    for cls_name in all_classes:
        lines.append(f'    "{cls_name}",')
    lines.append(")")
    lines.append("")

    init_file = schemas_dir / "__init__.py"
    init_file.write_text("\n".join(lines))
    print(f"  Regenerated {init_file}")


def verify_no_old_names(root: Path, info: dict) -> list:
    """Grep for any remaining old class/module names."""
    missed = []
    for old_cls in RENAME_MAP:
        old_mod, _ = info[old_cls]
        # Search for old class name
        result = subprocess.run(
            ["grep", "-r", "--include=*.py", "-l", rf"\b{old_cls}\b", str(root)],
            capture_output=True,
            text=True,
        )
        if result.stdout.strip():
            # Filter out this script itself and __pycache__
            files = [
                f
                for f in result.stdout.strip().split("\n")
                if "rename_schemas" not in f and "__pycache__" not in f
            ]
            if files:
                missed.append((old_cls, files))
    return missed


def main():
    root = Path(".")
    schemas_dir = root / "kraken_connector" / "schemas"
    api_dir = root / "kraken_connector" / "api"

    if not schemas_dir.exists():
        print("Error: Run from repository root")
        sys.exit(1)

    print("Validating mapping...")
    info = validate_mapping(schemas_dir)
    print(f"  {len(RENAME_MAP)} renames validated, no collisions")

    print("\nRenaming files...")
    rename_files(schemas_dir, info)

    print("\nUpdating file contents...")
    py_files = list(schemas_dir.glob("*.py")) + list(api_dir.rglob("*.py"))
    update_file_contents(py_files, info)

    print("\nRegenerating schemas/__init__.py...")
    regenerate_init(schemas_dir, info)

    print("\nVerifying no old names remain...")
    missed = verify_no_old_names(root / "kraken_connector", info)
    if missed:
        print("WARNING: Old names still found:")
        for old_cls, files in missed:
            print(f"  {old_cls}: {files}")
    else:
        print("  Clean — no old names found")

    print("\nDone! Run: pdm run pre-commit run -a && pdm run pytest -v")


if __name__ == "__main__":
    main()
