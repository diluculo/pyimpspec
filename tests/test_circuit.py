# pyimpspec is licensed under the GPLv3 or later (https://www.gnu.org/licenses/gpl-3.0.html).
# Copyright 2022 pyimpspec developers
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# The licenses of pyimpspec's dependencies and/or sources of portions of code are included in
# the LICENSES folder.

from unittest import TestCase
from collections import OrderedDict
from typing import (
    Dict,
    List,
    Tuple,
    Type,
    Union,
)
from numpy import (
    array,
    ndarray,
    allclose,
)
from sympy import Expr
from pyimpspec.circuit import (
    Circuit,
    CircuitBuilder,
    Parser,
    ParsingError,
    Connection,
    Parallel,
    Series,
    Element,
    Capacitor,
    ConstantPhaseElement,
    DeLevieFiniteLength,
    Gerischer,
    HavriliakNegami,
    HavriliakNegamiAlternative,
    Inductor,
    ModifiedInductor,
    Resistor,
    Warburg,
    WarburgOpen,
    WarburgShort,
    get_elements,
    parse_cdc,
)
from pyimpspec.circuit.parser import (
    ConnectionWithoutElements,
    DuplicateParameterDefinition,
    ExpectedNumericValue,
    ExpectedParameterIdentifier,
    InsufficientElementsInParallelConnection,
    InsufficientTokens,
    InvalidElementSymbol,
    InvalidParameterDefinition,
    InvalidParameterLowerLimit,
    InvalidParameterUpperLimit,
    TooManyParameterDefinitions,
    UnexpectedToken,
)


class TestElement(TestCase):
    def test_01_base_methods(self):
        symbol: str
        Class: Type[Element]
        for symbol, Class in get_elements().items():
            message: str = f"Element: {symbol}"
            element: Element = Class()
            self.assertNotEqual(
                element.get_extended_description(),
                "",
                msg=message,
            )
            self.assertNotEqual(element.get_description(), "", msg=message)
            self.assertTrue(
                element.get_description().startswith(symbol),
                msg=message,
            )

            defaults: Dict[str, float] = element.get_defaults()
            self.assertTrue(len(defaults) > 0, msg=message)
            for k, v in defaults.items():
                self.assertIsInstance(k, str, msg=message)
                self.assertIsInstance(v, float, msg=message)

            default_fixed: Dict[str, bool] = element.get_default_fixed()
            self.assertIsInstance(default_fixed, dict, msg=message)
            for k, v in default_fixed.items():
                self.assertIsInstance(k, str, msg=message)
                self.assertIsInstance(v, bool, msg=message)

            default_lower_limits: Dict[str, float] = element.get_default_lower_limits()
            self.assertIsInstance(default_fixed, dict, msg=message)
            for k, v in default_lower_limits.items():
                self.assertIsInstance(k, str, msg=message)
                self.assertIsInstance(v, float, msg=message)

            default_upper_limits: Dict[str, float] = element.get_default_upper_limits()
            self.assertIsInstance(default_fixed, dict, msg=message)
            for k, v in default_upper_limits.items():
                self.assertIsInstance(k, str, msg=message)
                self.assertIsInstance(v, float, msg=message)

            self.assertNotEqual(element.get_default_label(), "", msg=message)
            self.assertTrue(
                element.get_default_label().startswith(element.get_symbol()),
                msg=message,
            )
            self.assertTrue(
                element.get_label().startswith(element.get_symbol()),
                msg=message,
            )
            self.assertEqual(symbol, element.get_symbol(), msg=message)
            self.assertEqual(
                element.get_label(),
                element.get_default_label(),
                msg=message,
            )
            self.assertEqual(
                element.get_label(),
                element.get_symbol(),
                msg=message,
            )
            self.assertEqual(
                element.get_default_label(),
                element.get_symbol(),
                msg=message,
            )

            with self.assertRaises(AssertionError, msg=message):
                element._assign_identifier("5")
                element._assign_identifier(-4)
            self.assertEqual(element.get_identifier(), -1, msg=message)
            element._assign_identifier(8)
            self.assertEqual(element.get_identifier(), 8, msg=message)
            self.assertEqual(
                element.get_label(),
                element.get_symbol() + "_8",
                msg=message,
            )
            self.assertEqual(
                element.get_default_label(),
                element.get_symbol() + "_8",
                msg=message,
            )

            with self.assertRaises(AssertionError, msg=message):
                element.set_label(26)
            element.set_label("test")
            self.assertEqual(
                element.get_default_label(),
                element.get_symbol() + "_8",
                msg=message,
            )
            self.assertEqual(
                element.get_label(),
                element.get_symbol() + "_test",
                msg=message,
            )
            self.assertIn(":test}", element.to_string(1), msg=message)
            parameters: OrderedDict[str, float] = element.get_parameters()
            self.assertIsInstance(parameters, OrderedDict, msg=message)
            for k, v in parameters.items():
                self.assertIsInstance(k, str, msg=message)
                self.assertIsInstance(v, float, msg=message)

    def test_02_sympy(self):
        freq: List[float] = [1e-5, 1, 1e5]
        symbols: List[str] = list(get_elements().keys()) + [
            "K",
        ]
        symbol: str
        for symbol in symbols:
            message: str = f"Element: {symbol}"
            circuit: Circuit = parse_cdc(symbol)
            Z_regular: ndarray = circuit.impedances(freq)
            expr: Expr = circuit.to_sympy(substitute=True)
            Z_sympy: ndarray = array(
                list(map(lambda _: complex(expr.subs("f", _)), freq))
            )
            self.assertTrue(
                allclose(Z_regular.real, Z_sympy.real),
                msg=message,
            )
            self.assertTrue(
                allclose(Z_regular.imag, Z_sympy.imag),
                msg=message,
            )

    def test_03_get_elements(self):
        elements: Dict[str, Type[Element]] = get_elements()
        self.assertEqual(elements["R"], Resistor)
        self.assertEqual(elements["C"], Capacitor)
        self.assertEqual(elements["L"], Inductor)
        self.assertEqual(elements["La"], ModifiedInductor)
        self.assertEqual(elements["Q"], ConstantPhaseElement)
        self.assertEqual(elements["W"], Warburg)
        self.assertEqual(elements["Ws"], WarburgShort)
        self.assertEqual(elements["Wo"], WarburgOpen)
        self.assertEqual(elements["Ls"], DeLevieFiniteLength)
        self.assertEqual(elements["G"], Gerischer)
        self.assertEqual(elements["H"], HavriliakNegami)
        self.assertEqual(elements["Ha"], HavriliakNegamiAlternative)


# TODO: Create tests for the base Connection class
# TODO: Create tests for the Series and Parallel classes
class TestConnection(TestCase):
    def test_01_base_methods(self):
        pass

    def test_02_series(self):
        series: Series = Series([Resistor(R=250), Resistor(R=500)])
        self.assertEqual(series.impedance(1), 250 + 500)

    def test_03_parallel(self):
        parallel: Parallel = Parallel([Resistor(R=250), Resistor(R=500)])
        self.assertEqual(parallel.impedance(1), 1 / (1 / 250 + 1 / 500))


# TODO: Create tests for the Circuit class
class TestCircuit(TestCase):
    def test_01_parse_cdc(self):
        for symbol, Class in get_elements().items():
            circuit: Circuit = parse_cdc(symbol)
            elements: List[Union[Element, Connection]] = circuit.get_elements()
            self.assertEqual(len(elements), 1)
            self.assertEqual(type(elements[0]), Class)
            self.assertEqual(circuit.to_string(), f"[{symbol}]")

    def test_02_series(self):
        circuit: Circuit = parse_cdc("R{R=250}R{R=500}")
        self.assertEqual(circuit.impedance(1), 250 + 500)

    def test_03_parallel(self):
        circuit: Circuit = parse_cdc("(R{R=250}R{R=500})")
        self.assertEqual(circuit.impedance(1), 1 / (1 / 250 + 1 / 500))

    def test_04_elements(self):
        circuit: Circuit = parse_cdc("(RCQ)")
        elements: List[Union[Element, Connection]] = circuit.get_elements(
            flattened=False
        )
        self.assertEqual(type(elements), list)
        self.assertEqual(len(elements), 1)
        self.assertEqual(type(elements[0]), Series)
        elements = circuit.get_elements()
        self.assertEqual(type(elements), list)
        self.assertEqual(len(elements), 3)
        self.assertEqual(type(elements[0]), Resistor)
        self.assertEqual(type(elements[1]), Capacitor)
        self.assertEqual(type(elements[2]), ConstantPhaseElement)
        circuit = parse_cdc("R(RC)(RW)")
        elements = circuit.get_elements(flattened=False)
        self.assertEqual(type(elements), list)
        self.assertEqual(len(elements), 1)
        self.assertEqual(type(elements[0]), Series)
        elements = elements[0].get_elements(flattened=False)
        self.assertEqual(type(elements), list)
        self.assertEqual(len(elements), 3)
        self.assertEqual(type(elements[0]), Resistor)
        self.assertEqual(type(elements[1]), Parallel)
        self.assertEqual(type(elements[2]), Parallel)
        elements = circuit.get_elements()
        self.assertEqual(type(elements), list)
        self.assertEqual(len(elements), 5)
        self.assertEqual(type(elements[0]), Resistor)
        self.assertEqual(type(elements[1]), Resistor)
        self.assertEqual(type(elements[2]), Capacitor)
        self.assertEqual(type(elements[3]), Resistor)
        self.assertEqual(type(elements[4]), Warburg)
        self.assertEqual(type(circuit.get_element(0)), Resistor)
        self.assertEqual(type(circuit.get_element(4)), Warburg)
        self.assertEqual(circuit.get_element(4), elements[4])

    def test_05_connections(self):
        circuit: Circuit = parse_cdc("(RCQ)")
        connections: List[Connection] = circuit.get_connections(flattened=False)
        self.assertEqual(len(connections), 1)
        circuit = parse_cdc("R(RC)(RW)")
        connections = circuit.get_connections(flattened=False)
        self.assertEqual(len(connections), 1)
        connections = circuit.get_connections()
        self.assertEqual(len(connections), 3)


class TestCircuitBuilder(TestCase):
    def test_01_series(self):
        with CircuitBuilder() as builder:
            builder.add(Resistor())
            builder.add(Capacitor())
        self.assertEqual(builder.to_string(), "[RC]")
        with CircuitBuilder() as builder:
            builder += Resistor()
            builder += Capacitor()
        self.assertEqual(builder.to_string(), "[RC]")
        with self.assertRaises(AssertionError):
            with CircuitBuilder() as builder:
                pass

    def test_02_parallel(self):
        with CircuitBuilder(parallel=True) as builder:
            builder.add(Resistor())
            builder.add(Capacitor())
        self.assertEqual(builder.to_string(), "[(RC)]")
        with CircuitBuilder(parallel=True) as builder:
            builder += Resistor()
            builder += Capacitor()
        self.assertEqual(builder.to_string(), "[(RC)]")
        with self.assertRaises(AssertionError):
            with CircuitBuilder(parallel=True) as builder:
                builder.add(Resistor())
        with self.assertRaises(AssertionError):
            with CircuitBuilder(parallel=True) as builder:
                builder += Resistor()
        with self.assertRaises(AssertionError):
            with CircuitBuilder(parallel=True) as builder:
                pass

    def test_03_nested_connections(self):
        with CircuitBuilder() as builder:
            builder.add(Resistor())
            with builder.parallel() as parallel:
                parallel.add(Capacitor())
                parallel.add(Resistor())
        self.assertEqual(builder.to_string(), "[R(CR)]")
        with CircuitBuilder() as builder:
            builder += Resistor()
            with builder.parallel() as parallel:
                parallel += Capacitor()
                parallel += Resistor()
        self.assertEqual(builder.to_string(), "[R(CR)]")
        with CircuitBuilder() as builder:
            with builder.parallel() as parallel:
                parallel.add(Capacitor())
                parallel.add(Resistor())
            builder.add(Resistor())
        self.assertEqual(builder.to_string(), "[(CR)R]")
        with CircuitBuilder() as builder:
            with builder.parallel() as parallel:
                parallel += Capacitor()
                parallel += Resistor()
            builder += Resistor()
        self.assertEqual(builder.to_string(), "[(CR)R]")
        with CircuitBuilder() as builder:
            with builder.parallel() as parallel:
                with parallel.series() as series:
                    series.add(Resistor())
                    series.add(Capacitor())
                parallel.add(Resistor())
        self.assertEqual(builder.to_string(), "[([RC]R)]")
        with CircuitBuilder() as builder:
            with builder.parallel() as parallel:
                with parallel.series() as series:
                    series += Resistor()
                    series += Capacitor()
                parallel += Resistor()
        self.assertEqual(builder.to_string(), "[([RC]R)]")

    def test_04_parameters_and_labels(self):
        cdc: str = "[R{R=8.3E+01/2.0E+01/9.6E+01:test}C{C=4.0E-03F}]"
        with CircuitBuilder() as builder:
            R: Resistor = Resistor(R=83)
            R.set_lower_limit("R", 20)
            R.set_upper_limit("R", 96)
            R.set_label("test")
            builder.add(R)
            C: Capacitor = Capacitor(C=4e-3)
            C.set_fixed("C", True)
            builder.add(C)
        self.assertEqual(builder.to_string(1), cdc)
        with CircuitBuilder() as builder:
            builder += (
                Resistor(R=83)
                .set_lower_limit("R", 20)
                .set_upper_limit("R", 96)
                .set_label("test")
            )
            builder += Capacitor(C=4e-3).set_fixed("C", True)
        self.assertEqual(builder.to_string(1), cdc)


# TODO: Create tests for the Tokenizer class
class TestTokenizer(TestCase):
    def test_01_constructor(self):
        pass


class TestParser(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.valid_cdcs: List[str] = [
            "R",
            "RL",
            "(RL)",
            "([RL]C)",
            "(R[LC])",
            "(R[LC]W)",
            "(W[(RL)C])Q",
            "RLC",
            "RLCQ",
            "RLCQW",
            "(RLC)",
            "(RLCQ)",
            "(RLCQW)",
            "R(LCQW)",
            "RL(CQW)",
            "RLC(QW)",
            "(RLCQ)W",
            "(RLC)QW",
            "(RL)CQW",
            "R(LCQ)W",
            "R(LC)QW",
            "RL(CQ)W",
            "(R[WQ])",
            "(R[WQ]C)",
            "(R[W(LC)Q])",
            "([LC][RRQ])",
            "(R[WQ])([LC][RRQ])",
            "([RL][CW])",
            "R(RW)",
            "R(RW)C",
            "R(RWL)C",
            "R(RWL)(LQ)C",
            "R(RWL)C(LQ)",
            "R(LQ)C(RWL)",
            "R([RW]Q)C",
            "R(RW)(CQ)",
            "R([RW]Q[LRC])(CQ)",
            "R([RW][L(RQ)C]Q[LRC])(CQ)",
            "R([RW][L(WC)(RQ)C]Q[LRC])(CQ)",
            "(R[LCQW])",
            "(RL[CQW])",
            "(RLC[QW])",
            "(R[LCQ]W)",
            "(R[LC]QW)",
            "(RL[CQ]W)",
            "R(LC)(QW)",
            "(RL)C(QW)",
            "(RL)(CQ)W",
            "(RL)(CQW)",
            "(RLC)(QW)",
            "(R[LC])QW",
            "([RL]C)QW",
            "([RL]CQ)W",
            "([RL]CQW)",
            "([RLC]QW)",
            "([RLCQ]W)",
            "(R[(LC)QW])",
            "(R[L(CQ)W])",
            "(R[LC(QW)])",
            "(R[L(CQW)])",
            "(R[(LCQ)W])",
            "(R[(LC)Q]W)",
            "(R[L(CQ)]W)",
            "(RQ)RWL",
            "RWL(RQ)",
            "(R[QR])(LC)RW",
            "RW(LC)(RQ)",
            "RL(QW)L(RR)(RR)L(RR)C",
            "RL(QW)(L[(RR)(RR)L(RR)C])",
            "RL(QW)(L[(RR)(RR)L(RR)])",
        ]
        cls.invalid_cdcs: List[Tuple[str, ParsingError]] = [
            (
                "R[]",
                ConnectionWithoutElements,
            ),
            (
                "R()",
                ConnectionWithoutElements,
            ),
            (
                "Q{n=0.5, n=0.9}",
                DuplicateParameterDefinition,
            ),
            (
                "[R(RL{L=",
                ExpectedNumericValue,
            ),
            (
                "R{R=,}",
                ExpectedNumericValue,
            ),
            (
                "R{=5}",
                ExpectedParameterIdentifier,
            ),
            (
                "R(R)",
                InsufficientElementsInParallelConnection,
            ),
            (
                "R{R",
                InsufficientTokens,
            ),
            (
                "bA",
                InvalidElementSymbol,
            ),
            (
                "Vtpas",
                InvalidElementSymbol,
            ),
            (
                "R{Pqt=2}",
                InvalidParameterDefinition,
            ),
            (
                "R{R=3/4}",
                InvalidParameterLowerLimit,
            ),
            (
                "R{R=3//2}",
                InvalidParameterUpperLimit,
            ),
            (
                "R{R=5, n=0.5}",
                TooManyParameterDefinitions,
            ),
            (
                "R{R}",
                UnexpectedToken,
            ),
        ]

    def test_01_valid_cdcs(self):
        parser: Parser = Parser()
        freq: List[float] = [1e-5, 1, 1e5]
        cdc: str
        for cdc in self.valid_cdcs:
            circuit: Circuit = parser.process(cdc)
            Z_regular: ndarray = circuit.impedances(freq)
            expr: Expr = circuit.to_sympy(substitute=True)
            Z_sympy: ndarray = array(
                list(map(lambda _: complex(expr.subs("f", _)), freq))
            )
            self.assertTrue(allclose(Z_regular.real, Z_sympy.real))
            self.assertTrue(allclose(Z_regular.imag, Z_sympy.imag))
        for cdc in self.valid_cdcs:
            parse_cdc(cdc)

    def test_02_invalid_cdcs(self):
        parser: Parser = Parser()
        cdc: str
        error: ParsingError
        for (cdc, error) in self.invalid_cdcs:
            self.assertRaises(error, parser.process, cdc)
        for (cdc, error) in self.invalid_cdcs:
            self.assertRaises(error, parse_cdc, cdc)

    def test_03_nested_connections(self):
        CDCs: List[Tuple[str, str]] = [
            (
                "(R(LC))",
                "[(RLC)]",
            ),
            (
                "(R([LQ]C))",
                "[(R[LQ]C)]",
            ),
            (
                "[R[L][CQ]]",
                "[RLCQ]",
            ),
        ]
        parser: Parser = Parser()
        cdc_input: str
        cdc_output: str
        for (cdc_input, cdc_output) in CDCs:
            self.assertEqual(parser.process(cdc_input).to_string(), cdc_output)
