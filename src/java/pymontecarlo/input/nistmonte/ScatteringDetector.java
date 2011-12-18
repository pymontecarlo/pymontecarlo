package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.Electron;

import java.awt.event.ActionListener;

/**
 * Detector that requires to know if an electron is backscattered or
 * transmitted.
 * 
 * @author ppinard
 */
public interface ScatteringDetector extends Detector, ActionListener {

    /**
     * Sets the surface plane.A backscattered event is defined if an electron
     * exits above this plane whereas a transmitted event appends when an
     * electron exits below.
     * 
     * @param normal
     *            normal of the plane
     * @param point
     *            point on the plane
     */
    public void setSurfacePlane(double[] normal, double[] point);



    /**
     * Method called when an electron is backscattered.
     * 
     * @param electron
     *            electron
     */
    public void backscatterEvent(Electron electron);



    /**
     * Method called when an electron is transmitted.
     * 
     * @param electron
     *            electron
     */
    public void transmittedEvent(Electron electron);
}
