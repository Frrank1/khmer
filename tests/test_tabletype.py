"""
Tests for common features of *all* tables, including 1-bit presence/absence
tables.

This tests:

* method implementations in common between all "table types", including
  error handling code;
* basic API compatibility between all "table types", for methods with
  their own implementations.

Error handling & other class-specific code (e.g. in methods like
'load' and 'save' that are implemented differently for each type) will
be tested separately.  We can use code coverage to identify that
code...
"""

import pytest


from khmer import _Countgraph, _Counttable, _SmallCountgraph, _SmallCounttable
from khmer import _Nodegraph, _Nodetable

PRIMES_1m = [1000003, 1009837]


# all the table types!
@pytest.fixture(params=[_Countgraph, _Counttable, _SmallCountgraph,
                        _SmallCounttable, _Nodegraph, _Nodetable])
def tabletype(request):
    return request.param


def test_presence(tabletype):
    # basic get/add test
    tt = tabletype(12, PRIMES_1m)

    kmer = 'G' * 12
    hashval = tt.hash('G' * 12)

    assert tt.get(kmer) == 0
    assert tt.get(hashval) == 0

    tt.add(kmer)
    assert tt.get(kmer) == 1
    assert tt.get(hashval) == 1


def test_bad_create(tabletype):
    # creation should fail w/bad parameters
    try:
        tt = tabletype(5, [])
    except ValueError as err:
        assert 'tablesizes needs to be one or more numbers' in str(err)


def test_get_ksize(tabletype):
    # ksize() function.
    kh = tabletype(22, PRIMES_1m)
    assert kh.ksize() == 22


def test_hash(tabletype):
    # hashing of strings -> numbers.
    kh = tabletype(5, PRIMES_1m)
    x = kh.hash("ATGGC")
    assert type(x) == int


def test_reverse_hash(tabletype):
    # hashing of strings -> numbers.
    kh = tabletype(5, PRIMES_1m)

    try:
        x = kh.reverse_hash(15)
    except ValueError:
        pytest.skip("reverse_hash not implemented on this table type")

    assert type(x) == str


def test_hashsizes(tabletype):
    # hashsizes method.
    kh = tabletype(5, PRIMES_1m)
    assert kh.hashsizes() == PRIMES_1m


def test_add_hashval(tabletype):
    # test add(hashval)
    kh = tabletype(5, PRIMES_1m)
    x = kh.hash("ATGGC")
    y = kh.add(x)
    assert y

    z = kh.get(x)
    assert z == 1


def test_add_dna_kmer(tabletype):
    # test add(dna)
    kh = tabletype(5, PRIMES_1m)
    x = kh.add("ATGGC")
    assert x

    z = kh.get("ATGGC")
    assert z == 1


def test_get_hashval(tabletype):
    # test get(hashval)
    kh = tabletype(5, PRIMES_1m)
    hashval = kh.hash("ATGGC")
    kh.add(hashval)

    z = kh.get(hashval)
    assert z == 1


def test_get_dna_kmer(tabletype):
    # test get(dna)
    kh = tabletype(5, PRIMES_1m)
    hashval = kh.hash("ATGGC")
    kh.add(hashval)

    z = kh.get("ATGGC")
    assert z == 1


def test_get_kmer_counts(tabletype):
    hi = tabletype(6, PRIMES_1m)

    hi.consume("AAAAAA")
    counts = hi.get_kmer_counts("AAAAAA")
    print(counts)
    assert len(counts) == 1
    assert counts[0] == 1

    hi.consume("AAAAAA")
    counts = hi.get_kmer_counts("AAAAAA")
    print(counts)
    assert len(counts) == 1
    assert counts[0] >= 1

    hi.consume("AAAAAT")
    counts = hi.get_kmer_counts("AAAAAAT")
    print(counts)
    assert len(counts) == 2
    assert counts[0] >= 1
    assert counts[1] == 1


def test_get_kmer_hashes(tabletype):
    hi = tabletype(6, PRIMES_1m)

    hi.consume("AAAAAA")
    hashes = hi.get_kmer_hashes("AAAAAA")
    print(hashes)
    assert len(hashes) == 1
    assert hi.get(hashes[0]) == 1

    hi.consume("AAAAAT")
    hashes = hi.get_kmer_hashes("AAAAAAT")
    print(hashes)
    assert len(hashes) == 2
    assert hi.get(hashes[0]) >= 1
    assert hi.get(hashes[1]) == 1


def test_get_kmers(tabletype):
    hi = tabletype(6, PRIMES_1m)

    kmers = hi.get_kmers("AAAAAA")
    assert kmers == ["AAAAAA"]

    kmers = hi.get_kmers("AAAAAAT")
    assert kmers == ["AAAAAA", "AAAAAT"]

    kmers = hi.get_kmers("AGCTTTTC")
    assert kmers == ['AGCTTT', 'GCTTTT', 'CTTTTC']
