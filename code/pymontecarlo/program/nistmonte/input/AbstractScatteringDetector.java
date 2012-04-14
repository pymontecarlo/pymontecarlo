package pymontecarlo.program.nistmonte.input;

import gov.nist.microanalysis.EPQLibrary.EPQException;
import gov.nist.microanalysis.NISTMonte.Electron;
import gov.nist.microanalysis.NISTMonte.MonteCarloSS;
import gov.nist.microanalysis.Utility.Math2;

import java.awt.event.ActionEvent;
import java.util.Properties;

/**
 * Abstract detector that separates between backscatter and transmitted event.
 * 
 * @author ppinard
 */
public abstract class AbstractScatteringDetector extends ElectronDetector
        implements ScatteringDetector {

    @Override
    public void backscatterEvent(Electron electron) {
        // Do nothing
    }



    @Override
    public void transmittedEvent(Electron electron) {
        // Do nothing
    }

    /** Plane normal. */
    private double[] normal = Math2.Z_AXIS;

    /** Plane D coefficient in Ax + By + Cz + D = 0. */
    private double d = 0;



    @Override
    protected void saveAsProperties(Properties props) {
        super.saveAsProperties(props);

        props.setProperty("surfacePlane.a", Double.toString(normal[0]));
        props.setProperty("surfacePlane.b", Double.toString(normal[1]));
        props.setProperty("surfacePlane.c", Double.toString(normal[2]));
        props.setProperty("surfacePlane.d", Double.toString(d));
    }



    @Override
    public void actionPerformed(ActionEvent e) {
        super.actionPerformed(e);

        switch (e.getID()) {
        case MonteCarloSS.BackscatterEvent:
            Electron electron = ((MonteCarloSS) e.getSource()).getElectron();

            synchronized (this) {
                if (Math2.dot(normal, electron.getPosition()) + d > 0) {
                    backscatterEvent(electron);
                } else {
                    transmittedEvent(electron);
                }
            }

            break;
        default:
            break;
        }
    }



    @Override
    public void setSurfacePlane(double[] normal, double[] point) {
        this.normal = normal.clone();
        d = -normal[0] * point[0] - normal[1] * point[1] - normal[2] * point[2];
    }



    @Override
    public void setup(MonteCarloSS mcss) throws EPQException {
        mcss.addActionListener(this);
    }

}
