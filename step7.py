from abc import ABC


class Circuit(ABC):
    def __init__(self, name, num_inputs, num_outputs):
        self.name = name
        self.inputs = [Pin('input {} of {}'.format(i + 1, name)) for i in
                       range(num_inputs)]
        self.outputs = [Pin('output {} of {}'.format(i + 1, name)) for i in
                       range(num_outputs)]
        self.connections = []

    def process(self):
        raise NotImplementedError
        # can not call process(), it's an abstract method

    def set_input(self, num_input, state):
        self.inputs[num_input].set_state(state)



class And(Circuit):
    def __init__(self, name, num_inputs=2):
        super().__init__(name, num_inputs, 1)

    def process(self):
        result = True
        for pin_input in self.inputs:
            result = result and pin_input.is_state()
        self.outputs[0].set_state(result)


class Or(Circuit):
    def __init__(self, name, num_inputs=2):
        super().__init__(name, num_inputs, 1)

    def process(self):
        result = False
        for pin_input in self.inputs:
            result = result or pin_input.is_state()
        self.outputs[0].set_state(result)


class Not(Circuit):
    def __init__(self, name):
        super().__init__(name, 1, 1)

    def process(self):
        self.outputs[0].set_state(not self.inputs[0].is_state())


class Component(Circuit):
    def __init__(self, name, num_inputs, num_outputs):
        super().__init__(name, num_inputs, num_outputs)
        self.circuits = []

    def add_circuit(self, circuit):
        self.circuits.append(circuit)

    def process(self):
        for circuit in self.circuits:
            circuit.process()



class Observable(ABC):
    def __init__(self):
        self.observers = []

    def add_observer(self, observer):
        self.observers.append(observer)

    def remove_observer(self, observer):
        # TODO
        pass

    def notify_observers(self, an_object=None):
        for obs in self.observers:
            obs.update(self, an_object)
            # observable sends itself to each observer


class Observer(ABC):
    def update(self, observable, an_object):
        raise NotImplementedError
        # abstract method


class Pin(Observable, Observer):
    def __init__(self, name):
        super().__init__()
        self.name = name
        self.state = None

    def is_state(self):
        return self.state

    def set_state(self, new_state):
        self.state = new_state
        self.notify_observers(self)

    def update(self, observed_pin, an_object):
        self.set_state(observed_pin.is_state())


class Connection:
    def __init__(self, pin_from, pin_to):
        pin_from.add_observer(pin_to)


xor1 = Component('xor1', 2, 1)
or1 = Or('or1')
and1 = And('and1')
not1 = Not('not1')
and2 = And('and2')
# the order of adds will matter to simulation
xor1.add_circuit(or1) # more readable than xor.circuits.append(or)
xor1.add_circuit(and1)
xor1.add_circuit(not1)
xor1.add_circuit(and2)

Connection(xor1.inputs[0], and1.inputs[0])
Connection(xor1.inputs[0], or1.inputs[0])
Connection(xor1.inputs[1], and1.inputs[1])
Connection(xor1.inputs[1], or1.inputs[1])
Connection(or1.outputs[0], and2.inputs[0])
Connection(and1.outputs[0], not1.inputs[0])
Connection(not1.outputs[0], and2.inputs[1])
Connection(and2.outputs[0], xor1.outputs[0])

from copy import deepcopy

oneBitAdder = Component("OneBitAdder", 3, 2)
xor2 = deepcopy(xor1)
xor2.name = 'xor2'
and3 = And('and3')
and4 = And('and4') # or copy.deepcopy(and3) and rename
or2 = Or('or2')
# this order matters for the simulation
oneBitAdder.add_circuit(xor1)
oneBitAdder.add_circuit(xor2)
oneBitAdder.add_circuit(and3)
oneBitAdder.add_circuit(and4)
oneBitAdder.add_circuit(or2)

# connections "left to right"

A = oneBitAdder.inputs[0]
B = oneBitAdder.inputs[1]
Ci = oneBitAdder.inputs[2]
S = oneBitAdder.outputs[0]
Co = oneBitAdder.outputs[1]

input1Xor1 = xor1.inputs[0]
input2Xor1 = xor1.inputs[1]
outputXor1 = xor1.outputs[0]

input1Xor2 = xor2.inputs[0]
input2Xor2 = xor2.inputs[1]
outputXor2 = xor2.outputs[0]

input1And3 = and3.inputs[0]
input2And3 = and3.inputs[1]
outputAnd3 = and3.outputs[0]

input1And4 = and4.inputs[0]
input2And4 = and4.inputs[1]
outputAnd4 = and4.outputs[0]

input1Or2 = or2.inputs[0]
input2Or2 = or2.inputs[1]
outputOr2 = or2.outputs[0]

Connection(A, input1Xor1)
Connection(B, input2Xor1)
Connection(outputXor1, input1Xor2)
Connection(Ci, input2Xor2)
Connection(outputXor1, input1And3)
Connection(Ci, input2And3)
Connection(A, input1And4)
Connection(B, input2And4)
Connection(outputAnd3, input1Or2)
Connection(outputAnd4, input2Or2)
Connection(outputXor2, S)
Connection(outputOr2, Co)

inputs = []
for a in [False, True]:
    for b in [False, True]:
        for c in [False, True]:
            inputs.append([a,b,c])
expected_S = [False, True, True, False, True, False, False, True]
expected_Co = [False, False, False, True, False, True, True, True]

print("\t One bit loader testing:")
for (a, b, ci), exp_s, exp_co in zip(inputs, expected_S, expected_Co):
  A.set_state(a)
  B.set_state(b)
  Ci.set_state(ci)
  oneBitAdder.process()
  s = S.is_state()
  co = Co.is_state()
  print('{} + {} + {} = {}, {}'.format(a, b, ci, s, co))
  assert s == exp_s
  assert co == exp_co

one_bit_adder_1 = deepcopy(oneBitAdder)
one_bit_adder_1.name = 'one_bit_adder_1'
one_bit_adder_2 = deepcopy(oneBitAdder)
one_bit_adder_2.name = 'one_bit_adder_2'
one_bit_adder_3 = deepcopy(oneBitAdder)
one_bit_adder_3.name = 'one_bit_adder_3'
one_bit_adder_4 = deepcopy(oneBitAdder)
one_bit_adder_4.name = 'one_bit_adder_4'
four_bits_adder = Component("4bitsAdder", 9, 5)

four_bits_adder.add_circuit(one_bit_adder_1)
four_bits_adder.add_circuit(one_bit_adder_2)
four_bits_adder.add_circuit(one_bit_adder_3)
four_bits_adder.add_circuit(one_bit_adder_4)

A0 = four_bits_adder.inputs[0]
B0 = four_bits_adder.inputs[1]
A1 = four_bits_adder.inputs[2]
B1 = four_bits_adder.inputs[3]
A2 = four_bits_adder.inputs[4]
B2 = four_bits_adder.inputs[5]
A3 = four_bits_adder.inputs[6]
B3 = four_bits_adder.inputs[7]
Ci = four_bits_adder.inputs[8]
S0 = four_bits_adder.outputs[0]
S1 = four_bits_adder.outputs[1]
S2 = four_bits_adder.outputs[2]
S3 = four_bits_adder.outputs[3]
Co = four_bits_adder.outputs[4]

inputAbitAdder1 = one_bit_adder_1.inputs[0]
inputBbitAdder1 = one_bit_adder_1.inputs[1] 
inputCbitAdder1 = one_bit_adder_1.inputs[2]
outputSbitAdder1 = one_bit_adder_1.outputs[0]
outputCbitAdder1 = one_bit_adder_1.outputs[1]

inputAbitAdder2 = one_bit_adder_2.inputs[0]
inputBbitAdder2 = one_bit_adder_2.inputs[1] 
inputCbitAdder2 = one_bit_adder_2.inputs[2]
outputSbitAdder2 = one_bit_adder_2.outputs[0]
outputCbitAdder2 = one_bit_adder_2.outputs[1]

inputAbitAdder3 = one_bit_adder_3.inputs[0]
inputBbitAdder3 = one_bit_adder_3.inputs[1] 
inputCbitAdder3 = one_bit_adder_3.inputs[2]
outputSbitAdder3 = one_bit_adder_3.outputs[0]
outputCbitAdder3 = one_bit_adder_3.outputs[1]

inputAbitAdder4 = one_bit_adder_4.inputs[0]
inputBbitAdder4 = one_bit_adder_4.inputs[1] 
inputCbitAdder4 = one_bit_adder_4.inputs[2]
outputSbitAdder4 = one_bit_adder_4.outputs[0]
outputCbitAdder4 = one_bit_adder_4.outputs[1]

Connection(A0, inputAbitAdder1)
Connection(B0, inputBbitAdder1)
Connection(Ci, inputCbitAdder1)
Connection(outputSbitAdder1, S0)
Connection(outputCbitAdder1, inputCbitAdder2)

Connection(A1, inputAbitAdder2)
Connection(B1, inputBbitAdder2)
Connection(outputSbitAdder2, S1)
Connection(outputCbitAdder2, inputCbitAdder3)

Connection(A2, inputAbitAdder3)
Connection(B2, inputBbitAdder3)
Connection(outputSbitAdder3, S2)
Connection(outputCbitAdder3, inputCbitAdder4)

Connection(A3, inputAbitAdder4)
Connection(B3, inputBbitAdder4)
Connection(outputSbitAdder4, S3)
Connection(outputCbitAdder4, Co)

                                
inputs = []
expected_S = []
expected_Co = []
for x in range(512):
    n = [x//256%2, x//128%2, x//64%2, x//32%2, x//16%2, x//8%2, x//4%2, x//2%2 ,x%2]
    tf = [True if v == 1 else False for v in n]
    inputs.append(tf)
    expected_S.append('caca')
    expected_Co.append('caca')

"""
a3 = False
b3 = False
a2 = False
b2 = False
a1 = False
b1 = False
a0 = False
b0 = False
ci = False
A0.set_state(a0)
B0.set_state(b0)
A1.set_state(a1)
B1.set_state(b1)
A2.set_state(a2)
B2.set_state(b2)
A3.set_state(a3)
B3.set_state(b3)
Ci.set_state(ci)
four_bits_adder.process()
s0 = S0.is_state()
s1 = S1.is_state()
s2 = S2.is_state()
s3 = S3.is_state()
co = Co.is_state()
print('{} + {} + {} + {} + {} + {} + {} + {} + {} = {} {} {} {}, {}'.format(a3, b3, a2, b2, a1, b1, a0, b0, ci, s3, s2, s1, s0, co))
print(Ci.is_state(), inputCbitAdder1.is_state())
print('{} {} {} {}'.format(outputCbitAdder1.is_state(), outputCbitAdder2.is_state(), outputCbitAdder3.is_state(), outputCbitAdder4.is_state()))
"""
print("\t Four bit loader testing:")
for (a3, b3, a2, b2, a1, b1, a0, b0, ci), exp_s, exp_co in zip(inputs, expected_S, expected_Co):
    A0.set_state(a0)
    B0.set_state(b0)
    A1.set_state(a1)
    B1.set_state(b1)
    A2.set_state(a2)
    B2.set_state(b2)
    A3.set_state(a3)
    B3.set_state(b3)
    Ci.set_state(ci)
    four_bits_adder.process()
    s0 = S0.is_state()
    s1 = S1.is_state()
    s2 = S2.is_state()
    s3 = S3.is_state()
    co = Co.is_state()
    print('{} + {} + {} + {} + {} + {} + {} + {} + {} = {} {} {} {}, {}'.format(a3, b3, a2, b2, a1, b1, a0, b0, ci, s3, s2, s1, s0, co))


    #assert s == exp_s
    #assert co == exp_co

four_bits_adder_1 = deepcopy(four_bits_adder)
four_bits_adder_1.name = 'four_bits_adder_1'
four_bits_adder_2 = deepcopy(four_bits_adder)
four_bits_adder_2.name = 'four_bits_adder_2'
eight_bits_adder = Component("8bitsAdder", 17, 9)

eight_bits_adder.add_circuit(four_bits_adder_1)
eight_bits_adder.add_circuit(four_bits_adder_2)

Ae0 = eight_bits_adder.inputs[0]
Ae1 = eight_bits_adder.inputs[1]
Ae2 = eight_bits_adder.inputs[2]
Ae3 = eight_bits_adder.inputs[3]
Ae4 = eight_bits_adder.inputs[4]
Ae5 = eight_bits_adder.inputs[5]
Ae6 = eight_bits_adder.inputs[6]
Ae7 = eight_bits_adder.inputs[7]
Be0 = eight_bits_adder.inputs[8]
Be1 = eight_bits_adder.inputs[9]
Be2 = eight_bits_adder.inputs[10]
Be3 = eight_bits_adder.inputs[11]
Be4 = eight_bits_adder.inputs[12]
Be5 = eight_bits_adder.inputs[13]
Be6 = eight_bits_adder.inputs[14]
Be7 = eight_bits_adder.inputs[15]
Cei = eight_bits_adder.inputs[16]

Se0 = eight_bits_adder.outputs[0]
Se1 = eight_bits_adder.outputs[1]
Se2 = eight_bits_adder.outputs[2]
Se3 = eight_bits_adder.outputs[3]
Se4 = eight_bits_adder.outputs[4]
Se5 = eight_bits_adder.outputs[5]
Se6 = eight_bits_adder.outputs[6]
Se7 = eight_bits_adder.outputs[7]
Ceo = eight_bits_adder.outputs[8]

inputA0fourAdder1 = four_bits_adder_1.inputs[0]
inputA1fourAdder1 = four_bits_adder_1.inputs[2]
inputA2fourAdder1 = four_bits_adder_1.inputs[4]
inputA3fourAdder1 = four_bits_adder_1.inputs[6]
inputB0fourAdder1 = four_bits_adder_1.inputs[1]
inputB1fourAdder1 = four_bits_adder_1.inputs[3]
inputB2fourAdder1 = four_bits_adder_1.inputs[5]
inputB3fourAdder1 = four_bits_adder_1.inputs[7]
inputCifourAdder1 = four_bits_adder_1.inputs[8]

outputS0fourAdder1 = four_bits_adder_1.outputs[0]
outputS1fourAdder1 = four_bits_adder_1.outputs[1]
outputS2fourAdder1 = four_bits_adder_1.outputs[2]
outputS3fourAdder1 = four_bits_adder_1.outputs[3]
outputCfourAdder1 = four_bits_adder_1.outputs[4]

inputA0fourAdder2 = four_bits_adder_2.inputs[0]
inputA1fourAdder2 = four_bits_adder_2.inputs[2]
inputA2fourAdder2 = four_bits_adder_2.inputs[4]
inputA3fourAdder2 = four_bits_adder_2.inputs[6]
inputB0fourAdder2 = four_bits_adder_2.inputs[1]
inputB1fourAdder2 = four_bits_adder_2.inputs[3]
inputB2fourAdder2 = four_bits_adder_2.inputs[5]
inputB3fourAdder2 = four_bits_adder_2.inputs[7]
inputCifourAdder2 = four_bits_adder_2.inputs[8]

outputS0fourAdder2 = four_bits_adder_2.outputs[0]
outputS1fourAdder2 = four_bits_adder_2.outputs[1]
outputS2fourAdder2 = four_bits_adder_2.outputs[2]
outputS3fourAdder2 = four_bits_adder_2.outputs[3]
outputCfourAdder2 = four_bits_adder_2.outputs[4]

Connection(Ae0, inputA0fourAdder1)
Connection(Ae1, inputA1fourAdder1)
Connection(Ae2, inputA2fourAdder1)
Connection(Ae3, inputA3fourAdder1)
Connection(Be0, inputB0fourAdder1)
Connection(Be1, inputB1fourAdder1)
Connection(Be2, inputB2fourAdder1)
Connection(Be3, inputB3fourAdder1)

Connection(Cei, inputCifourAdder1)

Connection(outputS0fourAdder1, Se0)
Connection(outputS1fourAdder1, Se1)
Connection(outputS2fourAdder1, Se2)
Connection(outputS3fourAdder1, Se3)

Connection(Ae4, inputA0fourAdder2)
Connection(Ae5, inputA1fourAdder2)
Connection(Ae6, inputA2fourAdder2)
Connection(Ae7, inputA3fourAdder2)
Connection(Be4, inputB0fourAdder2)
Connection(Be5, inputB1fourAdder2)
Connection(Be6, inputB2fourAdder2)
Connection(Be7, inputB3fourAdder2)

Connection(outputCfourAdder1, inputCifourAdder2)

Connection(outputS0fourAdder2, Se4)
Connection(outputS1fourAdder2, Se5)
Connection(outputS2fourAdder2, Se6)
Connection(outputS3fourAdder2, Se7)

Connection(outputCfourAdder2, Ceo)

inputs = []

for x in range(131072):
    n = [x//65536%2, x//32768%2, x//16383%2, x//8192%2, x//4096%2, x//2048%2, x//1024%2 ,x//512%2, x//256%2, x//128%2, x//64%2, x//32%2, x//16%2, x//8%2, x//4%2, x//2%2 ,x%2]
    tf = [True if v == 1 else False for v in n]
    inputs.append(tf)

    
print("\t Eight bit loader testing:")
for (b7, b6, b5, b4, b3, b2, b1, b0, a7, a6, a5, a4, a3, a2, a1, a0, ci) in inputs:
    Ae0.set_state(a0)
    Ae1.set_state(a1)
    Ae2.set_state(a2)
    Ae3.set_state(a3)
    Ae4.set_state(a4)
    Ae5.set_state(a5)
    Ae6.set_state(a6)
    Ae7.set_state(a7)
    Be0.set_state(b0)
    Be1.set_state(b1)
    Be2.set_state(b2)
    Be3.set_state(b3)
    Be4.set_state(b4)
    Be5.set_state(b5)
    Be6.set_state(b6)
    Be7.set_state(b7)
    Cei.set_state(ci)
    
    eight_bits_adder.process()
    s0 = Se0.is_state()
    s1 = Se1.is_state()
    s2 = Se2.is_state()
    s3 = Se3.is_state()
    s4 = Se4.is_state()
    s5 = Se5.is_state()
    s6 = Se6.is_state()
    s7 = Se7.is_state()
    co = Ceo.is_state()
    print('{} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} + {} = {} {} {} {} {} {} {} {}, {}'.format(b7, b6, b5, b4, b3, b2, b1, b0, a7, a6, a5, a4, a3, a2, a1, a0, ci, s7, s6, s5, s4, s3, s2, s1, s0, co))
