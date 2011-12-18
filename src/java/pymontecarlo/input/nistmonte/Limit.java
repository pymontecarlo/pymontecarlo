package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

/**
 * Interface for all limits.
 * 
 * @author ppinard
 */
public interface Limit {

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

}
