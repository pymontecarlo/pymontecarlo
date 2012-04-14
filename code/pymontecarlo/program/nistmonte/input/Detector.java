package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.awt.event.ActionListener;
import java.io.IOException;
import java.util.zip.ZipOutputStream;

/**
 * Interface for all detectors.
 * 
 * @author ppinard
 */
public interface Detector extends ActionListener {

    /**
     * Setups the simulation and other listeners. This typically involves adding
     * action listeners to collect data for this detector. Note that the x-ray
     * and Bremsstrahlung event listener may be <code>null</code> if no x-ray
     * have to be detected.
     * 
     * @param mcss
     *            Monte Carlo simulation
     * @param xrel
     *            x-ray event listener
     * @param bel
     *            Bremsstrahlung event listener
     * @throws EPQException
     *             if an error occurs during the setup
     */
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) throws EPQException;



    /**
     * Saves the data collected by the detector inside a ZIP.
     * 
     * @param zipOutput
     *            ZIP output stream where to save the results
     * @param key
     *            key of the detector
     * @throws IOException
     *             if an error occurs while saving the results
     */
    public void saveResults(ZipOutputStream zipOutput, String key)
            throws IOException;



    /**
     * Saves a log of the detector parameters inside a ZIP.
     * 
     * @param zipOutput
     *            ZIP output stream where to save the results
     * @param key
     *            key of the detector
     * @throws IOException
     *             if an error occurs while saving the log
     */
    public void saveLog(ZipOutputStream zipOutput, String key)
            throws IOException;



    /**
     * Method called at the start of a new simulation.
     */
    public void reset();



    /**
     * Returns the tag of the result class of this detector.
     * 
     * @return tag of the result class for this detector
     */
    public String getTag();
}
