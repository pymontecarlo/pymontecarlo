package pymontecarlo.input.nistmonte;

import gov.nist.microanalysis.NISTMonte.BremsstrahlungEventListener;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.NISTMonte.XRayEventListener2;

import java.awt.event.ActionEvent;
import java.awt.event.ActionListener;

/**
 * Limit the number of showers.
 * 
 * @author ppinard
 */
public class ShowersLimit implements Limit, ActionListener {

    /** Maximum number of trajectories. */
    private final int maxShowers;



    /**
     * Creates a new <code>ShowersLimit</code>.
     * 
     * @param showers
     *            maximum number of trajectories
     */
    public ShowersLimit(int showers) {
        if (showers <= 0)
            throw new IllegalArgumentException(
                    "Maximum number of trajectories must be greater than 0");
        this.maxShowers = showers;
    }



    /**
     * Returns the maximum number of showers.
     * 
     * @return maximum number of showers
     */
    public int getMaximumShowers() {
        return maxShowers;
    }



    @Override
    public void setup(MonteCarloSS mcss, XRayEventListener2 xrel,
            BremsstrahlungEventListener bel) {
        throw new RuntimeException("Should not be added");
    }



    @Override
    public void actionPerformed(ActionEvent e) {

    }
}
