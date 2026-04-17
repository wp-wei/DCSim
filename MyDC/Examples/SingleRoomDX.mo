within MyDC.Examples;
model SingleRoomDX
  "Minimal air-cooled DC thermal model with aggregate IT load and simple cooling"
  extends Modelica.Icons.Example;

  parameter Modelica.Units.SI.HeatCapacity C_room = 8e6
    "Lumped room thermal capacity [J/K]";
  parameter Modelica.Units.SI.ThermalResistance R_amb = 0.003
    "Room to ambient resistance [K/W]";
  parameter Modelica.Units.SI.Temperature T_amb = 303.15
    "Ambient/boundary temperature [K]";
  parameter Modelica.Units.SI.Power Q_it_base = 4000
    "Base IT heat gain [W]";
  parameter Modelica.Units.SI.Power Q_it_step = 3000
    "Additional IT pulse gain [W]";
  parameter Real k_cool = 600
    "Simple proportional cooling gain [W/K]";
  parameter Modelica.Units.SI.Temperature T_set = 297.15
    "Cooling control setpoint [K]";

  Modelica.Thermal.HeatTransfer.Components.HeatCapacitor roomAir(
    C = C_room,
    T(start = 299.15, fixed = true))
    "Aggregated room air thermal mass";

  Modelica.Thermal.HeatTransfer.Components.ThermalResistor toAmbient(R = R_amb)
    "Envelope heat exchange";

  Modelica.Thermal.HeatTransfer.Sources.FixedTemperature ambient(T = T_amb)
    "Ambient boundary";

  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow itHeat
    "Aggregated IT heat source";

  Modelica.Thermal.HeatTransfer.Sources.PrescribedHeatFlow coolingHeat
    "Simple cooling sink (negative heat flow)";

  Modelica.Blocks.Sources.Pulse itPulse(
    amplitude = Q_it_step,
    period = 7200,
    width = 50,
    offset = Q_it_base,
    startTime = 1800)
    "IT load variation";

  Modelica.Blocks.Math.Add dT(k1 = 1, k2 = -1)
    "Room temp minus setpoint";

  Modelica.Blocks.Math.Gain coolGain(k = -k_cool)
    "Cooling command (negative to remove heat)";

  Modelica.Blocks.Nonlinear.Limiter coolLimiter(uMax = 0, uMin = -12000)
    "Limit cooling capacity";

  Modelica.Blocks.Sources.Constant setpoint(k = T_set);

  output Modelica.Units.SI.Temperature TRoom = roomAir.T
    "Representative room air temperature";
  output Modelica.Units.SI.Power QIT = itPulse.y
    "IT load";
  output Modelica.Units.SI.Power QCool = coolingHeat.Q_flow
    "Cooling heat flow (negative removes heat)";

equation
  connect(roomAir.port, toAmbient.port_a);
  connect(toAmbient.port_b, ambient.port);
  connect(itHeat.port, roomAir.port);
  connect(coolingHeat.port, roomAir.port);

  connect(itPulse.y, itHeat.Q_flow);
  connect(roomAir.T, dT.u1);
  connect(setpoint.y, dT.u2);
  connect(dT.y, coolGain.u);
  connect(coolGain.y, coolLimiter.u);
  connect(coolLimiter.y, coolingHeat.Q_flow);

  annotation(
    experiment(StartTime = 0, StopTime = 21600, Tolerance = 1e-6, Interval = 60),
    Documentation(info = "Minimal robust thermal response example for headless OpenModelica execution."));
end SingleRoomDX;
