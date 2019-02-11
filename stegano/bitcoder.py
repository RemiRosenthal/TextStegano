from bitstring import Bits

UTF_ENCODING = "utf-8"


class BitCoder:
    @staticmethod
    def text_to_bits(text, encoding=UTF_ENCODING, errors="surrogatepass"):
        bits = bin(int.from_bytes(text.encode(encoding, errors), 'big'))[2:]
        return bits.zfill(8 * ((len(bits) + 7) // 8))

    @staticmethod
    def text_from_bits(bits, encoding=UTF_ENCODING, errors="surrogatepass"):
        n = int(bits, 2)
        return n.to_bytes((n.bit_length() + 7) // 8, 'big').decode(encoding, errors) or '\0'

    @staticmethod
    def trim_bits(bits: Bits) -> Bits:
        leftover_length = bits.length % 8
        return bits[:bits.length-leftover_length]
