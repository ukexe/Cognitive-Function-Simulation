from brian2 import *

# Neuron parameters
Cm = 200 * pF
gL = 10 * nS
EL = -70 * mV
VT = -50 * mV
DeltaT = 2 * mV
Vcut = VT + 5 * DeltaT

# Neuron model equation
eqs = '''
dv/dt = (gL * (EL - v) + gL * DeltaT * exp((v - VT) / DeltaT) + I_syn) / Cm : volt (unless refractory)
I_syn : ampere
'''

# Synapse model
tau_syn = 5 * ms
eqs_syn = '''
dw/dt = (Apre * Apost) / tau_syn - w / tau_syn : 1 (clock-driven)
Apre : volt
Apost : volt
'''

# STDP parameters
tau = 20 * ms
Apre = 0.01
Apost = -Apre * 1.05
wmax = 1.0

# Neuron Groups
N = 1000
source = NeuronGroup(N, eqs, threshold='v > Vcut', reset='v = EL', refractory=5 * ms, method='exponential_euler')
target = NeuronGroup(N, eqs, threshold='v > Vcut', reset='v = EL', refractory=5 * ms, method='exponential_euler')

# Initialize neuron parameters
source.v = EL + (VT - EL) * rand(len(source))
target.v = EL + (VT - EL) * rand(len(target))

# Synapses
source_target_conn = Synapses(source, target, model=eqs_syn,
                              on_pre='''Apre += 0.01 * volt
                                        w = clip(w + Apost, 0, wmax)''',
                              on_post='''Apost += 0.01 * volt
                                         w = clip(w + Apre, 0, wmax)''')
source_target_conn.connect(p=0.1)

# Initialize synaptic weights
source_target_conn.w = 'rand() * wmax'

# Simulation
run_duration = 1 * second
run(run_duration, report='text')

# Plotting
figure(figsize=(12, 8))

# Raster plot for source population
subplot(2, 1, 1)
plot(source_mon.t / ms, source_mon.i, '.k')
title('Source Population')
xlabel('Time (ms)')
ylabel('Neuron index')

# Raster plot for target population
subplot(2, 1, 2)
plot(target_mon.t / ms, target_mon.i, '.r')
title('Target Population')
xlabel('Time (ms)')
ylabel('Neuron index')

# Show plot
show()

# Visualization of membrane potential and synaptic currents
figure(figsize=(12, 8))

# Membrane potential of source population
subplot(2, 2, 1)
plot(source_state_mon.t / ms, source_state_mon.v.T / mV)
title('Membrane Potential - Source Population')
xlabel('Time (ms)')
ylabel('Membrane Potential (mV)')

# Membrane potential of target population
subplot(2, 2, 2)
plot(target_state_mon.t / ms, target_state_mon.v.T / mV)
title('Membrane Potential - Target Population')
xlabel('Time (ms)')
ylabel('Membrane Potential (mV)')

# Synaptic currents of source population
subplot(2, 2, 3)
plot(source_state_mon.t / ms, source_state_mon.I_syn.T / nA)
title('Synaptic Currents - Source Population')
xlabel('Time (ms)')
ylabel('Synaptic Current (nA)')

# Synaptic currents of target population
subplot(2, 2, 4)
plot(target_state_mon.t / ms, target_state_mon.I_syn.T / nA)
title('Synaptic Currents - Target Population')
xlabel('Time (ms)')
ylabel('Synaptic Current (nA)')

# Show plot
show()