import hashlib
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

DIFFICULTY = 4  # Number of leading zeros required


def _compute_hash(index, timestamp, data, prev_hash, nonce):
    """Compute SHA-256 hash for a block."""
    block_str = json.dumps({
        'index': index,
        'timestamp': timestamp,
        'data': data,
        'prev_hash': prev_hash,
        'nonce': nonce
    }, sort_keys=True)
    return hashlib.sha256(block_str.encode()).hexdigest()


def proof_of_work(index, timestamp, data, prev_hash):
    """Find nonce such that hash starts with DIFFICULTY zeros."""
    nonce = 0
    target = '0' * DIFFICULTY
    while True:
        h = _compute_hash(index, timestamp, data, prev_hash, nonce)
        if h.startswith(target):
            return nonce, h
        nonce += 1
        if nonce > 1000000:
            raise RuntimeError(f"Proof of work failed to converge after {nonce} iterations")


def add_block(issue_id, action, data, app=None):
    """Add a new block to the chain for an issue. Returns the created BlockchainRecord."""
    from models.blockchain import BlockchainRecord
    from models import db

    ctx = None
    if app:
        ctx = app.app_context()
        ctx.push()

    try:
        last = BlockchainRecord.query.filter_by(issue_id=issue_id).order_by(BlockchainRecord.block_index.desc()).first()
        if last:
            prev_hash = last.data_hash
            block_index = last.block_index + 1
        else:
            prev_hash = '0' * 64
            block_index = 0

        timestamp = datetime.utcnow().isoformat()
        data_str = json.dumps(data, sort_keys=True) if isinstance(data, dict) else str(data)
        nonce, block_hash = proof_of_work(block_index, timestamp, data_str, prev_hash)
        block_timestamp = datetime.fromisoformat(timestamp)

        record = BlockchainRecord(
            issue_id=issue_id,
            action=action,
            data_hash=block_hash,
            prev_hash=prev_hash,
            nonce=nonce,
            block_index=block_index,
            timestamp=block_timestamp
        )
        db.session.add(record)
        db.session.commit()
        logger.info("Blockchain block added: issue=%s action=%s index=%d hash=%s",
                    issue_id, action, block_index, block_hash[:16])
        return record
    except Exception as e:
        logger.error("Blockchain error: %s", e)
        db.session.rollback()
        raise
    finally:
        if ctx:
            ctx.pop()


def validate_chain(issue_id):
    """Validate the integrity of the blockchain for an issue."""
    from models.blockchain import BlockchainRecord

    records = BlockchainRecord.query.filter_by(issue_id=issue_id).order_by(BlockchainRecord.block_index).all()
    if not records:
        return True, "No blocks to validate"

    for i, record in enumerate(records):
        if record.block_index != i:
            return False, f"Block {i} has wrong index {record.block_index}"
        if i == 0:
            expected_prev = '0' * 64
        else:
            expected_prev = records[i-1].data_hash
        if record.prev_hash != expected_prev:
            return False, f"Block {i} has invalid prev_hash"
        if not record.data_hash.startswith('0' * DIFFICULTY):
            return False, f"Block {i} hash does not meet difficulty requirement"
    return True, "Chain is valid"


def get_chain_for_issue(issue_id):
    """Return all blocks for an issue as a list of dicts."""
    from models.blockchain import BlockchainRecord
    records = BlockchainRecord.query.filter_by(issue_id=issue_id).order_by(BlockchainRecord.block_index).all()
    return [r.to_dict() for r in records]


def verify_block(block_id):
    """Verify a single block."""
    from models.blockchain import BlockchainRecord
    record = BlockchainRecord.query.get(block_id)
    if not record:
        return False, "Block not found"
    if not record.data_hash.startswith('0' * DIFFICULTY):
        return False, "Hash does not meet difficulty"
    return True, "Block is valid"
