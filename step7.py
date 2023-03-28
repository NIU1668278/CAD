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

import copy

oneBitAdder = Component("OneBitAdder", 3, 2)
xor2 = copy.deepcopy(xor1)
xor2.name = 'xor2'
and3 = And('and3')
and4 = And('and4') # or copy.deepcopy(and3) and rename
or2 = Or('or2');
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
Co = oneBitAdder.inputs[1]

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