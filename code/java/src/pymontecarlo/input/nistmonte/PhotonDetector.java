package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.Utility.Math2;

import java.util.Properties;

/**
 * Abstract class of all photon detectors.
 * 
 * @author ppinard
 */
public abstract class PhotonDetector extends AbstractDetector {

    /** Position of the detector in meters. */
    private final double[] detectorPosition;



    /**
     * Creates a new <code>PhotonDetector</code>.
     * 
     * @param takeOffAngle
     *            elevation from the x-y plane (in radians)
     * @param azimuthAngle
     *            counter-clockwise angle from the positive x-axis in the x-y
     *            plane (in radians)
     */
    public PhotonDetector(double takeOffAngle, double azimuthAngle) {
        double[] pos =
                new double[] { 1.0, Math.tan(azimuthAngle),
                        Math.tan(takeOffAngle) };
        detectorPosition =
                Math2.multiply(0.999 * MonteCarloSS.ChamberRadius,
                        Math2.normalize(pos));
    }



    /**
     * Creates a new <code>PhotonDetector</code>.
     * 
     * @param pos
     *            detector position in the chamber (in meters)
     */
    public PhotonDetector(double[] pos) {
        if (Math2.dot(pos, pos) >= Math.pow(MonteCarloSS.ChamberRadius, 2.0))
            throw new IllegalArgumentException(
                    "Detector position is outside the chamber. The chamber has a maximum radius of "
                            + MonteCarloSS.ChamberRadius + " m");
        detectorPosition = pos.clone();
    }



    /**
     * Returns the detector position in the chamber (in meters).
     * 
     * @return detector position (in meters)
     */
    public double[] getDetectorPosition() {
        return detectorPosition;
    }



    /**
     * Returns the take-off angle of the detector (in radians). This corresponds
     * to the elevation angle from the x-y plane.
     * 
     * @return take-off angle (in radians)
     */
    public double getTakeOffAngle() {
        return Math.atan2(detectorPosition[2], detectorPosition[0]);
    }



    /**
     * Returns the azimuth angle of the detector (in radians). This corresponds
     * to the counter-clockwise angle from the positive x-axis in the x-y plane.
     * 
     * @return azimuth angle (in radians)
     */
    public double getAzimuthAngle() {
        return Math.atan2(detectorPosition[1], detectorPosition[0]);
    }



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        props.setProperty("detectorPosition.x",
                Double.toString(detectorPosition[0]));
        props.setProperty("detectorPosition.y",
                Double.toString(detectorPosition[1]));
        props.setProperty("detectorPosition.z",
                Double.toString(detectorPosition[2]));
        props.setProperty("takeOffAngle", Double.toString(getTakeOffAngle()));
        props.setProperty("azimuthAngle", Double.toString(getAzimuthAngle()));
    }



    /**
     * Returns whether the detector requires generation of Bremsstrahlung
     * x-rays.
     * 
     * @return <code>true</code> if Bremstrahlung x-rays should be generated,
     *         <code>false</code> otherwise
     */
    public abstract boolean requiresBremsstrahlung();
}
